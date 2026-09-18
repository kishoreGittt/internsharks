from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Task26 Async AI Jobs"

    openrouter_api_key: str
    openrouter_model: str = "openai/gpt-oss-20b:free"
    openrouter_base_url: str = (
        "https://openrouter.ai/api/v1"
    )

    worker_count: int = 2

    simulated_processing_delay_seconds: float = 0
    simulate_ai_failure: bool = False

    max_file_size: int = 10 * 1024 * 1024

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()