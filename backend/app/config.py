from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Application
    app_name: str = "Shubham Khanapure Portfolio API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "https://*.vercel.app",
    ]

    # Database
    database_url: str = ""
    database_pool_size: int = 3  # Small pool for serverless
    database_max_overflow: int = 0
    database_pool_recycle: int = 3600  # 1 hour
    database_pool_pre_ping: bool = True

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_times: int = 5  # 5 submissions
    rate_limit_seconds: int = 3600  # per hour

    # CORS
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_allow_headers: List[str] = ["*"]

    # Feature Flags
    use_json_storage: bool = False  # Fallback to JSON if database is unavailable

    # Email Service (Resend)
    resend_api_key: str = ""
    resend_from_email: str = "onboarding@resend.dev"
    resend_to_email: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Dependency for getting settings in FastAPI routes"""
    return settings
