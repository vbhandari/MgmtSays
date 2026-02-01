"""Application settings using Pydantic Settings management."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "MgmtSays"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    log_level: str = "INFO"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default=["http://localhost:5173", "http://localhost:3000"])

    # Database
    postgres_user: str = "mgmtsays"
    postgres_password: str = "mgmtsays_dev"
    postgres_db: str = "mgmtsays"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    database_url: str | None = None

    # Vector Store (ChromaDB)
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chroma_auth_token: str = "dev_token"

    # LLM Providers
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    default_llm_provider: Literal["openai", "anthropic"] = "openai"
    openai_model: str = "gpt-4-turbo-preview"
    anthropic_model: str = "claude-3-opus-20240229"
    embedding_model: str = "text-embedding-3-small"

    # File Storage
    storage_backend: Literal["local", "s3"] = "local"
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 50

    # S3 (optional)
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_region: str = "us-east-1"
    s3_bucket_name: str | None = None

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period_seconds: int = 60

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def database_dsn(self) -> str:
        """Get the database connection string."""
        if self.database_url:
            # Handle SQLite URLs
            if self.database_url.startswith("sqlite"):
                return self.database_url.replace("sqlite://", "sqlite+aiosqlite://")
            return self.database_url
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def sync_database_dsn(self) -> str:
        """Get synchronous database connection string (for Alembic)."""
        if self.database_url:
            if self.database_url.startswith("sqlite"):
                return self.database_url
            return self.database_url.replace("+asyncpg", "")
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
