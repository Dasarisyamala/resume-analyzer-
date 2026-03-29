from __future__ import annotations

import json
from datetime import datetime

from werkzeug.security import generate_password_hash

from database import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class User(db.Model, TimestampMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="admin")

    @classmethod
    def create(cls, email: str, password: str, role: str = "admin") -> "User":
        user = cls(
            email=email.lower(),
            password_hash=generate_password_hash(password),
            role=role,
        )
        db.session.add(user)
        return user


class Resume(db.Model, TimestampMixin):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(255))
    stored_filename = db.Column(db.String(255))
    file_path = db.Column(db.String(255))
    content_type = db.Column(db.String(120))

    name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    education = db.Column(db.Text)
    experience = db.Column(db.Text)
    summary = db.Column(db.Text)
    years_experience = db.Column(db.Float)

    parsed_text = db.Column(db.Text)
    domain = db.Column(db.String(120), default="General")
    skills = db.Column(db.Text)  # JSON encoded list
    domain_evidence = db.Column(db.Text)

    matches = db.relationship(
        "MatchResult",
        back_populates="resume",
        cascade="all, delete-orphan",
    )
    skill_entries = db.relationship(
        "ResumeSkill",
        back_populates="resume",
        cascade="all, delete-orphan",
    )

    @property
    def skills_list(self) -> list[str]:
        try:
            return json.loads(self.skills) if self.skills else []
        except json.JSONDecodeError:
            return []

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "filename": self.original_filename,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "education": self.education,
            "experience": self.experience,
            "summary": self.summary,
            "domain": self.domain,
            "years_experience": self.years_experience,
            "skills": self.skills_list,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ResumeSkill(db.Model, TimestampMixin):
    __tablename__ = "resume_skills"

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    weight = db.Column(db.Float, default=1.0)

    resume = db.relationship("Resume", back_populates="skill_entries")


class JobRequirement(db.Model, TimestampMixin):
    __tablename__ = "job_requirements"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    domain = db.Column(db.String(120))
    description = db.Column(db.Text)
    min_experience = db.Column(db.Float)
    required_skills = db.Column(db.Text)  # JSON list
    keywords = db.Column(db.Text)  # JSON list

    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_by = db.relationship("User")

    matches = db.relationship(
        "MatchResult",
        back_populates="job_requirement",
        cascade="all, delete-orphan",
    )

    @property
    def required_skills_list(self) -> list[str]:
        try:
            return json.loads(self.required_skills) if self.required_skills else []
        except json.JSONDecodeError:
            return []

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "domain": self.domain,
            "description": self.description,
            "min_experience": self.min_experience,
            "required_skills": self.required_skills_list,
            "keywords": json.loads(self.keywords or "[]"),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class MatchResult(db.Model, TimestampMixin):
    __tablename__ = "match_results"

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False)
    job_requirement_id = db.Column(
        db.Integer, db.ForeignKey("job_requirements.id"), nullable=False
    )
    score = db.Column(db.Float, nullable=False)
    matched_skills = db.Column(db.Text)
    matched_keywords = db.Column(db.Text)
    breakdown = db.Column(db.Text)

    resume = db.relationship("Resume", back_populates="matches")
    job_requirement = db.relationship("JobRequirement", back_populates="matches")

    def to_dict(self) -> dict:
        def _loads(value: str | None) -> list[str]:
            if not value:
                return []
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return []

        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "job_requirement_id": self.job_requirement_id,
            "score": self.score,
            "matched_skills": _loads(self.matched_skills),
            "matched_keywords": _loads(self.matched_keywords),
            "breakdown": json.loads(self.breakdown or "{}"),
        }
