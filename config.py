import os


class Config:
    """Centralized Flask configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///database.db",  # fallback for local development
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File uploads
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB per file

    # Allowed resume extensions
    ALLOWED_EXTENSIONS = {".pdf", ".docx"}

    # Resume scoring weights
    SKILL_WEIGHT = float(os.getenv("SKILL_WEIGHT", 0.5))
    KEYWORD_WEIGHT = float(os.getenv("KEYWORD_WEIGHT", 0.3))
    EXPERIENCE_WEIGHT = float(os.getenv("EXPERIENCE_WEIGHT", 0.2))
