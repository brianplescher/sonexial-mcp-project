"""Configuration management using pydantic-settings."""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    env: str = "development"

    # HTTP Server
    host: str = "0.0.0.0"
    port: int = 8080

    # Database
    database_url: str = "sqlite+aiosqlite:///./sonexial.db"

    # Authentication
    api_key: str = "change-me"
    auth_disabled: bool = True

    # Logging
    log_level: str = "INFO"

    # CORS
    cors_origins: str = "*"

    model_config = SettingsConfigDict(
        env_prefix="SONEXIAL_MCP_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    @property
    def is_production(self) -> bool:
        return self.env == "production"

    @property
    def is_development(self) -> bool:
        return self.env == "development"

    @property
    def cors_origins_list(self) -> list[str]:
        if self.cors_origins == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",")]


def get_settings() -> Settings:
    """Get application settings singleton."""
    return Settings()
