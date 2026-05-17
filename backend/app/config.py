"""Application settings.

All values can be overridden via environment variables (``.env`` for local
development, Vercel project env vars in production). Knowledge-hub settings
live under the ``knowledge_*`` namespace so they cannot collide with future
portfolio settings.
"""

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # ── Application ──────────────────────────────────────────────────────────
    app_name: str = "Shubham Khanapure Portfolio API"
    app_version: str = "1.0.0"
    debug: bool = False

    # ── Security ─────────────────────────────────────────────────────────────
    secret_key: str = "dev-secret-key-change-in-production"
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "https://*.vercel.app",
    ]

    # ── Database ─────────────────────────────────────────────────────────────
    database_url: str = ""
    database_pool_size: int = 3
    database_max_overflow: int = 0
    database_pool_recycle: int = 3600
    database_pool_pre_ping: bool = True

    # ── Rate limiting ────────────────────────────────────────────────────────
    rate_limit_enabled: bool = True
    rate_limit_times: int = 5
    rate_limit_seconds: int = 3600

    # ── CORS ─────────────────────────────────────────────────────────────────
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_allow_headers: List[str] = ["*"]

    # ── Feature flags ────────────────────────────────────────────────────────
    use_json_storage: bool = False

    # ── Email (Resend) ───────────────────────────────────────────────────────
    resend_api_key: str = ""
    resend_from_email: str = "onboarding@resend.dev"
    resend_to_email: str = ""

    # ── Knowledge hub ────────────────────────────────────────────────────────
    knowledge_content_dir: str = "app/content"
    knowledge_jwt_secret_key: str = "change-me-in-production"
    knowledge_jwt_algorithm: str = "HS256"
    knowledge_jwt_expire_hours: int = 24
    knowledge_admin_username: str = "admin"
    knowledge_admin_password: str = "change-me-in-production"
    knowledge_enable_watcher: bool = False
    knowledge_enable_agent: bool = False
    knowledge_index_on_boot: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    # Helpful predicates so callers don't need to parse the URL themselves.
    @property
    def is_postgres(self) -> bool:
        return self.database_url.startswith(
            ("postgresql://", "postgresql+asyncpg://")
        )


settings = Settings()


def get_settings() -> Settings:
    """FastAPI dependency for retrieving settings inside routes."""
    return settings
