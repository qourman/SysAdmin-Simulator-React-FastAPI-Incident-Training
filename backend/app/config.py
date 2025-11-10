from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="SysAdmin Simulator API", alias="APP_NAME")
    api_prefix: str = Field(default="/api", alias="API_PREFIX")
    allowed_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        alias="ALLOWED_ORIGINS",
    )
    session_timeout_seconds: int = Field(default=60 * 60, alias="SESSION_TIMEOUT_SECONDS")

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def split_origins(cls, value: List[str] | str) -> List[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
