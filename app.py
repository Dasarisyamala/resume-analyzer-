from __future__ import annotations

import json
from datetime import timedelta
from functools import wraps
from typing import Dict, List, Tuple

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from werkzeug.exceptions import BadRequest
from werkzeug.security import check_password_hash

from config import Config
from database import db, init_app as init_db
from interviewer import generate_questions
from models import JobRequirement, MatchResult, Resume, User
from services.matching import persist_match, score_resume_against_job
from services.resume_processing import process_resume_file

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
init_db(app)
app.permanent_session_lifetime = timedelta(days=7)


def current_user() -> User | None:
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
                return jsonify({"error": "Authentication required"}), 401
            next_url = request.full_path if request.method == "GET" else url_for("home")
            if next_url.endswith("?"):
                next_url = next_url[:-1]
            return redirect(url_for("login", next=next_url))
        return func(*args, **kwargs)

    return wrapper


@app.context_processor
def inject_user():
    return {"current_user": current_user()}


def _scoring_weights() -> Dict[str, float]:
    return {
        "skill": app.config["SKILL_WEIGHT"],
        "keyword": app.config["KEYWORD_WEIGHT"],
        "experience": app.config["EXPERIENCE_WEIGHT"],
    }


def _normalize_domain_scores(domain_scores: Dict[str, int]) -> List[Dict[str, float]]:
    if not domain_scores:
        return []
    max_score = max(domain_scores.values()) or 1
    ordered = sorted(domain_scores.items(), key=lambda item: item[1], reverse=True)
    return [
        {
            "domain": domain,
            "value": round((score / max_score) * 100, 1),
        }
        for domain, score in ordered
    ]


def _resume_score(domain_scores: Dict[str, int], match: MatchResult | None) -> float:
    if match:
        return round(match.score, 1)
    if not domain_scores:
        return 0.0
    max_score = max(domain_scores.values())
    return round(min(100.0, max_score * 12), 1)


def _improvement_tips(
    skills: List[str], match: MatchResult | None, resume_score: float
) -> List[str]:
    tips: List[str] = []
    skill_set = {skill.lower() for skill in skills}

    if match and match.job_requirement:
        required = match.job_requirement.required_skills_list
        missing = [
            skill
            for skill in required
            if skill.lower() not in skill_set
        ]
        if missing:
            tips.append(
                "Highlight projects using "
                + ", ".join(missing[:3])
                + f" to align with {match.job_requirement.title}."
            )
        if match.score < 80:
            tips.append("Add measurable achievements to strengthen your ATS score.")

    if resume_score < 70:
        tips.append("Include quantifiable impact statements for major projects.")
    if len(skills) < 5:
        tips.append("Expand the skills section with tools, frameworks, or certifications.")

    if not tips:
        tips.append("Great work! Keep the resume updated with recent wins.")

    return tips


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user():
        return redirect(url_for("home"))

    error = None
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        confirm = request.form.get("confirm_password") or ""

        if not email or not password:
            error = "Email and password are required."
        elif password != confirm:
            error = "Passwords do not match."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        elif User.query.filter_by(email=email).first():
            error = "Account already exists for this email."
        else:
            user = User.create(email=email, password=password)
            db.session.commit()
            session["user_id"] = user.id
            session.permanent = True
            next_url = (
                request.form.get("next")
                or request.args.get("next")
                or url_for("home")
            )
            return redirect(next_url)

    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user():
        return redirect(url_for("home"))

    error = None
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            error = "Invalid email or password."
        else:
            session["user_id"] = user.id
            session.permanent = True
            next_url = (
                request.form.get("next")
                or request.args.get("next")
                or url_for("home")
            )
            return redirect(next_url)

    return render_template("login.html", error=error)


@app.get("/logout")
@login_required
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))


def _build_result_payload(
    resume: Resume,
    diagnostics: Dict[str, Dict],
    match: MatchResult | None,
) -> Dict:
    payload = {
        "resume": resume.to_dict(),
        "skills": diagnostics.get("skills", []),
        "domain_scores": diagnostics.get("domain_scores", {}),
        "questions": generate_questions(diagnostics.get("skills", [])),
    }

    if match:
        match_data = match.to_dict()
        match_data["job"] = match.job_requirement.to_dict()
        payload["match"] = match_data

    domain_scores = payload["domain_scores"]
    resume_score = _resume_score(domain_scores, match)
    payload.update(
        {
            "resume_score": resume_score,
            "domain_progress": _normalize_domain_scores(domain_scores),
            "tips": _improvement_tips(payload["skills"], match, resume_score),
            "domain_label": resume.domain or "General",
        }
    )

    return payload


def _process_files(files, job_id: int | None) -> Tuple[List[Dict], List[Dict]]:
    if not files:
        raise BadRequest("No files were provided")

    processed: List[Dict] = []
    errors: List[Dict] = []
    job = JobRequirement.query.get(job_id) if job_id else None

    for file in files:
        if file.filename.strip() == "":
            errors.append({"filename": "", "error": "Empty filename"})
            continue

        try:
            resume, diagnostics = process_resume_file(
                file,
                app.config["UPLOAD_FOLDER"],
                app.config["ALLOWED_EXTENSIONS"],
            )

            match_model = None
            if job:
                score, details = score_resume_against_job(
                    resume, job, _scoring_weights()
                )
                match_model = persist_match(resume, job, score, details)

            db.session.commit()
            processed.append(_build_result_payload(resume, diagnostics, match_model))
        except ValueError as exc:
            db.session.rollback()
            errors.append({"filename": file.filename, "error": str(exc)})

    return processed, errors


@app.route("/")
@login_required
def home():
    stats = {
        "resume_count": Resume.query.count(),
        "job_count": JobRequirement.query.count(),
    }
    recent_resumes = Resume.query.order_by(Resume.created_at.desc()).limit(5).all()
    jobs = JobRequirement.query.order_by(JobRequirement.created_at.desc()).all()
    return render_template(
        "index.html",
        stats=stats,
        resumes=recent_resumes,
        jobs=jobs,
    )


@app.post("/upload")
@login_required
def upload():
    files = request.files.getlist("resume")
    job_id = request.form.get("job_id", type=int)
    processed, errors = _process_files(files, job_id)

    status = 200 if processed else 400
    return (
        render_template("result.html", results=processed, errors=errors),
        status,
    )


@app.post("/upload_resume")
@login_required
def upload_resume_api():
    files = request.files.getlist("resume")
    job_id = request.form.get("job_id", type=int) or request.args.get(
        "job_id", type=int
    )
    processed, errors = _process_files(files, job_id)

    if not processed and errors:
        status = 400
    elif processed and errors:
        status = 207  # multi-status when partial failures
    else:
        status = 201

    return jsonify({"processed": processed, "errors": errors}), status


@app.get("/resumes")
@login_required
def list_resumes():
    domain = request.args.get("domain")
    skill = request.args.get("skill")
    min_experience = request.args.get("min_experience", type=float)

    query = Resume.query
    if domain:
        query = query.filter(Resume.domain.ilike(f"%{domain}%"))
    if min_experience is not None:
        query = query.filter(Resume.years_experience >= min_experience)

    resumes = query.order_by(Resume.created_at.desc()).all()
    if skill:
        skill_lower = skill.lower()
        resumes = [
            r for r in resumes if skill_lower in {s.lower() for s in r.skills_list}
        ]

    return jsonify([r.to_dict() for r in resumes])


@app.route("/job_requirements", methods=["GET", "POST"])
@login_required
def job_requirements():
    if request.method == "GET":
        jobs = JobRequirement.query.order_by(JobRequirement.created_at.desc()).all()
        return jsonify([job.to_dict() for job in jobs])

    payload = request.get_json(force=True)
    title = payload.get("title")
    if not title:
        raise BadRequest("Job title is required")

    job = JobRequirement(
        title=title,
        domain=payload.get("domain"),
        description=payload.get("description"),
        min_experience=payload.get("min_experience"),
        required_skills=json.dumps(payload.get("required_skills", [])),
        keywords=json.dumps(payload.get("keywords", [])),
    )
    db.session.add(job)
    db.session.commit()
    return jsonify(job.to_dict()), 201


@app.get("/filtered_resumes")
@login_required
def filtered_resumes():
    job_id = request.args.get("job_id", type=int)
    if not job_id:
        raise BadRequest("job_id is required")

    job = JobRequirement.query.get_or_404(job_id)
    min_score = request.args.get("min_score", type=float, default=0.0)
    domain_filter = request.args.get("domain")

    query = Resume.query
    if domain_filter:
        query = query.filter(Resume.domain.ilike(f"%{domain_filter}%"))

    resume_entries = query.all()
    weights = _scoring_weights()
    results = []
    for resume in resume_entries:
        score, details = score_resume_against_job(resume, job, weights)
        match = persist_match(resume, job, score, details)
        if score >= min_score:
            data = {
                "resume": resume.to_dict(),
                "score": score,
                "details": details,
                "match_id": match.id,
            }
            results.append(data)

    results.sort(key=lambda item: item["score"], reverse=True)
    db.session.commit()
    return jsonify({"job": job.to_dict(), "results": results})


@app.get("/top_candidates")
@login_required
def top_candidates():
    job_id = request.args.get("job_id", type=int)
    limit = request.args.get("limit", default=5, type=int)
    if not job_id:
        raise BadRequest("job_id is required")

    job = JobRequirement.query.get_or_404(job_id)
    min_score = request.args.get("min_score", type=float, default=0.0)

    weights = _scoring_weights()
    scores: List[Tuple[Resume, float, Dict]] = []
    for resume in Resume.query.all():
        score, details = score_resume_against_job(resume, job, weights)
        persist_match(resume, job, score, details)
        if score >= min_score:
            scores.append((resume, score, details))

    db.session.commit()
    scores.sort(key=lambda item: item[1], reverse=True)
    top = [
        {
            "resume": resume.to_dict(),
            "score": score,
            "details": details,
        }
        for resume, score, details in scores[:limit]
    ]

    return jsonify({"job": job.to_dict(), "top_candidates": top})


@app.get("/history")
@login_required
def history():
    resumes = Resume.query.order_by(Resume.created_at.desc()).limit(50).all()
    payload = []
    for resume in resumes:
        domain_scores = {}
        if resume.domain_evidence:
            try:
                domain_scores = json.loads(resume.domain_evidence)
            except json.JSONDecodeError:
                domain_scores = {}

        skills = resume.skills_list
        resume_score = _resume_score(domain_scores, None)
        payload.append(
            {
                "resume": resume.to_dict(),
                "skills": skills,
                "domain_scores": domain_scores,
                "domain_label": resume.domain or "General",
                "questions": generate_questions(skills),
                "resume_score": resume_score,
                "domain_progress": _normalize_domain_scores(domain_scores),
                "tips": _improvement_tips(skills, None, resume_score),
                "match": None,
            }
        )
    return render_template("result.html", results=payload, errors=[])


if __name__ == "__main__":
    app.run(debug=True)