from __future__ import annotations

import json
import os
import uuid
from typing import Dict, List, Tuple

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from database import db
from models import Resume, ResumeSkill
from parser import extract_text
from services.domain_classifier import classify_domain
from services.text_parsing import parse_resume_details
from skills import extract_skills


def _allowed_file(filename: str, allowed_extensions: set[str]) -> bool:
    _, ext = os.path.splitext(filename.lower())
    return ext in allowed_extensions


def _persist_skills(resume: Resume, skills: List[str]) -> None:
    for skill in skills:
        entry = ResumeSkill(resume_id=resume.id, name=skill)
        db.session.add(entry)


def process_resume_file(
    file_storage: FileStorage,
    upload_dir: str,
    allowed_extensions: set[str],
) -> Tuple[Resume, Dict[str, List[str]]]:
    if file_storage.filename == "":
        raise ValueError("Empty filename provided")

    if not _allowed_file(file_storage.filename, allowed_extensions):
        raise ValueError("Unsupported file type")

    os.makedirs(upload_dir, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex}_{secure_filename(file_storage.filename)}"
    file_path = os.path.join(upload_dir, unique_name)
    file_storage.save(file_path)

    text = extract_text(file_path)
    if not text or text.startswith("[PARSE_ERROR]") or text.startswith("[PDF_ERROR]"):
        raise ValueError(text or "Unable to read file")

    details = parse_resume_details(text)
    skills = extract_skills(text)
    domain, domain_scores = classify_domain(skills, text)

    resume = Resume(
        original_filename=file_storage.filename,
        stored_filename=unique_name,
        file_path=file_path,
        content_type=file_storage.mimetype,
        name=details.get("name"),
        email=details.get("email"),
        phone=details.get("phone"),
        education=details.get("education"),
        experience=details.get("experience"),
        summary=details.get("summary"),
        years_experience=details.get("years_experience"),
        parsed_text=text,
        domain=domain,
        skills=json.dumps(skills),
        domain_evidence=json.dumps(domain_scores),
    )
    db.session.add(resume)
    db.session.flush()

    _persist_skills(resume, skills)

    return resume, {"skills": skills, "domain_scores": dict(domain_scores)}
