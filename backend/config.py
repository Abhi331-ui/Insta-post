import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load .env file from project root or backend directory
env_path = Path(__file__).resolve().parent.parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).resolve().parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()


class Settings:
    PROJECT_NAME: str = "PromptPulse"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").strip().lower()

    # AI Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "gemini").lower()

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    if not DATABASE_URL and ENVIRONMENT != "production":
        DATABASE_URL = "sqlite:///./promptpulse.db"

    # Redis & Task Queue
    REDIS_URL: str = os.getenv("REDIS_URL", "")
    if not REDIS_URL and ENVIRONMENT != "production":
        REDIS_URL = "redis://localhost:6379/0"

    # Meta / Instagram Graph API
    META_APP_ID: str = os.getenv("META_APP_ID", "")
    META_APP_SECRET: str = os.getenv("META_APP_SECRET", "")
    INSTAGRAM_REDIRECT_URI: str = os.getenv("INSTAGRAM_REDIRECT_URI", "")
    if not INSTAGRAM_REDIRECT_URI and ENVIRONMENT != "production":
        INSTAGRAM_REDIRECT_URI = "http://localhost:3000/settings/instagram/callback"
    INSTAGRAM_USER_ID: str = os.getenv("INSTAGRAM_USER_ID", "")
    INSTAGRAM_ACCESS_TOKEN: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")

    # Storage
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "supabase")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_STORAGE_BUCKET: str = os.getenv("SUPABASE_STORAGE_BUCKET", "slides")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "promptpulse-media")
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY", "")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY", "")
    S3_REGION: str = os.getenv("S3_REGION", "us-east-1")

    # Media Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    MEDIA_DIR: Path = BASE_DIR / "media"
    SLIDES_DIR: Path = BASE_DIR / "media" / "slides"
    PUBLIC_MEDIA_BASE_URL: str = os.getenv("PUBLIC_MEDIA_BASE_URL", "")
    if not PUBLIC_MEDIA_BASE_URL and ENVIRONMENT != "production":
        PUBLIC_MEDIA_BASE_URL = "http://localhost:8000/media"

    # Auth & Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    if not SECRET_KEY and ENVIRONMENT != "production":
        SECRET_KEY = "dev-secret-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080")
    )
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "")
    if not FRONTEND_URL and ENVIRONMENT != "production":
        FRONTEND_URL = "http://localhost:3000"

    # Brand Defaults (Updated Dark/Cinematic Design System)
    BRAND_NAME: str = "PromptPulse"
    PRIMARY_COLOR: str = "#7C3AED"
    BACKGROUND_COLOR: str = "#000000"
    TEXT_COLOR: str = "#FFFFFF"
    SECONDARY_COLOR: str = "#D1D5DB"
    ACCENT_CYAN: str = "#06B6D4"
    BUTTON_PRIMARY: str = "#5B21B6"
    WHITE_COLOR: str = "#FFFFFF"
    FONT_FAMILY: str = "Inter, sans-serif"

    # Slide Specs
    SLIDE_WIDTH: int = 1080
    SLIDE_HEIGHT: int = 1350
    TOTAL_SLIDES: int = 6


settings = Settings()

if settings.ENVIRONMENT == "production":
    required_by_production = {
        "DATABASE_URL": settings.DATABASE_URL,
        "SECRET_KEY": settings.SECRET_KEY,
        "FRONTEND_URL": settings.FRONTEND_URL,
        "PUBLIC_MEDIA_BASE_URL": settings.PUBLIC_MEDIA_BASE_URL,
        "INSTAGRAM_REDIRECT_URI": settings.INSTAGRAM_REDIRECT_URI,
        "SUPABASE_URL": settings.SUPABASE_URL,
        "SUPABASE_SERVICE_ROLE_KEY": settings.SUPABASE_SERVICE_ROLE_KEY,
    }
    for name, value in required_by_production.items():
        if not value:
            raise RuntimeError(f"{name} must be configured in production")
    if settings.DATABASE_URL.startswith("sqlite"):
        raise RuntimeError("Production must not use SQLite. Configure Supabase PostgreSQL via DATABASE_URL.")
    if "localhost" in settings.FRONTEND_URL or "localhost" in settings.PUBLIC_MEDIA_BASE_URL or "localhost" in settings.INSTAGRAM_REDIRECT_URI:
        raise RuntimeError("Production URLs must not point to localhost. Configure the deployed Render/Vercel values instead.")

# Ensure media and slide output directories exist
settings.MEDIA_DIR.mkdir(parents=True, exist_ok=True)
settings.SLIDES_DIR.mkdir(parents=True, exist_ok=True)
