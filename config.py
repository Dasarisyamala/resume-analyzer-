import os


class Config:
    """Centralized Flask configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    
    # Database migration logic for production
    _DB_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")
    if _DB_URL.startswith("postgres://"):
        _DB_URL = _DB_URL.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = _DB_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File uploads
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 128 * 1024 * 1024))
    MAX_FILES_PER_UPLOAD = int(os.getenv("MAX_FILES_PER_UPLOAD", 50))

    # Allowed resume extensions
    ALLOWED_EXTENSIONS = {".pdf", ".docx"}

    # Storage backend
    STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local").lower()
    DELETE_LOCAL_AFTER_CLOUD_UPLOAD = (
        os.getenv("DELETE_LOCAL_AFTER_CLOUD_UPLOAD", "true").lower() == "true"
    )

    # AWS S3 configuration (used when STORAGE_BACKEND=s3)
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
    AWS_S3_PREFIX = os.getenv("AWS_S3_PREFIX", "resumes")

    # Resume scoring weights
    SKILL_WEIGHT = float(os.getenv("SKILL_WEIGHT", 0.5))
    KEYWORD_WEIGHT = float(os.getenv("KEYWORD_WEIGHT", 0.3))
    EXPERIENCE_WEIGHT = float(os.getenv("EXPERIENCE_WEIGHT", 0.2))
