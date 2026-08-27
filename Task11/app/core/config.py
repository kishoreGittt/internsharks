from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MONGO_URI: str = Field(..., min_length=1)
    DATABASE_NAME: str = Field(..., min_length=1)

    JWT_SECRET_KEY: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = Field(default="HS256")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, gt=0)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, gt=0)

    APP_ENV: str = Field(default="development")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @field_validator("JWT_ALGORITHM")
    @classmethod
    def validate_algorithm(cls, value: str) -> str:
        allowed = {"HS256", "HS384", "HS512"}

        if value not in allowed:
            raise ValueError(
                f"JWT_ALGORITHM must be one of: {', '.join(allowed)}"
            )

        return value

    @field_validator("APP_ENV")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        allowed = {"development", "testing", "production"}

        if value not in allowed:
            raise ValueError(
                f"APP_ENV must be one of: {', '.join(allowed)}"
            )

        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()