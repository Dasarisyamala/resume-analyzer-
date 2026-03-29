from __future__ import annotations

import json
from typing import Dict, List, Tuple

from database import db
from models import JobRequirement, MatchResult, Resume


def _load_json_list(value: str | None) -> List[str]:
    if not value:
        return []
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return []


def _normalize_keywords(keywords: List[str]) -> List[str]:
    return [kw.strip().lower() for kw in keywords if kw.strip()]


def score_resume_against_job(
    resume: Resume,
    job: JobRequirement,
    weights: Dict[str, float],
) -> Tuple[float, Dict[str, List[str]]]:
    resume_skills = resume.skills_list
    job_skills = _load_json_list(job.required_skills)
    job_keywords = _normalize_keywords(_load_json_list(job.keywords))
    resume_text = (resume.parsed_text or "").lower()

    matched_skills = sorted(set(resume_skills) & set(job_skills))
    matched_keywords = sorted([kw for kw in job_keywords if kw in resume_text])

    skill_score = (len(matched_skills) / len(job_skills)) if job_skills else 1.0
    keyword_score = (
        len(matched_keywords) / len(job_keywords)
        if job_keywords
        else 1.0
    )
    if job.min_experience and resume.years_experience:
        experience_ratio = min(resume.years_experience / job.min_experience, 1.0)
    elif job.min_experience:
        experience_ratio = 0.0
    else:
        experience_ratio = 1.0

    overall_score = (
        skill_score * weights["skill"]
        + keyword_score * weights["keyword"]
        + experience_ratio * weights["experience"]
    )

    details = {
        "matched_skills": matched_skills,
        "matched_keywords": matched_keywords,
        "skill_score": round(skill_score * 100, 2),
        "keyword_score": round(keyword_score * 100, 2),
        "experience_score": round(experience_ratio * 100, 2),
    }

    return round(overall_score * 100, 2), details


def persist_match(
    resume: Resume,
    job: JobRequirement,
    score: float,
    details: Dict[str, List[str]],
) -> MatchResult:
    match = MatchResult.query.filter_by(
        resume_id=resume.id, job_requirement_id=job.id
    ).one_or_none()

    if match is None:
        match = MatchResult(
            resume=resume,
            job_requirement=job,
            score=score,
            matched_skills=json.dumps(details["matched_skills"]),
            matched_keywords=json.dumps(details["matched_keywords"]),
            breakdown=json.dumps(details),
        )
        db.session.add(match)
    else:
        match.score = score
        match.matched_skills = json.dumps(details["matched_skills"])
        match.matched_keywords = json.dumps(details["matched_keywords"])
        match.breakdown = json.dumps(details)

    db.session.flush()
    return match
