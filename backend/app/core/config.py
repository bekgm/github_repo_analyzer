from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: Literal["development", "staging", "production"] = "development"
    app_debug: bool = True
    app_secret_key: str = "change-me-in-production"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "analyzer"
    postgres_password: str = "analyzer_secret"
    postgres_db: str = "github_analyzer"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def sync_database_url(self) -> str:
        """Used by Alembic and Celery (synchronous drivers)."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    redis_url: str = "redis://localhost:6379/0"

    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    github_token: str = ""
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"

    rate_limit_per_minute: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()
