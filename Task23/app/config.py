from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


# =========================================================
# Project paths
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


# =========================================================
# Model pricing
# =========================================================

MODEL_PRICING = {
    "openai/gpt-oss-20b:free": {
        "input_per_token": 0.0,
        "output_per_token": 0.0,
    },
    "local-mock": {
        "input_per_token": 0.0,
        "output_per_token": 0.0,
    },
}


# =========================================================
# Application settings
# =========================================================

class Settings(BaseSettings):
    """
    Central configuration for Task23.
    """

    # -----------------------------------------------------
    # Application
    # -----------------------------------------------------

    app_name: str = "Task23 Evaluation API"

    app_version: str = "1.0.0"

    debug: bool = True

    # -----------------------------------------------------
    # MongoDB
    # -----------------------------------------------------

    mongodb_url: str = "mongodb+srv://kishorerajavel003_db_user:0kBzppKAJiTBcJMu@cluster0.wnmsgxj.mongodb.net/?appName=Cluster0"

    mongodb_database: str = "task23_evaluations"

    mongodb_collection: str = "evaluation_runs"

    # -----------------------------------------------------
    # OpenRouter
    # -----------------------------------------------------

    openrouter_api_key: Optional[str] = None

    openrouter_base_url: str = (
        "https://openrouter.ai/api/v1"
    )

    openrouter_model: str = (
        "openai/gpt-oss-20b:free"
    )

    # -----------------------------------------------------
    # Judge
    # -----------------------------------------------------

    judge_enabled: bool = False

    judge_model: str = (
        "openai/gpt-oss-20b:free"
    )

    # -----------------------------------------------------
    # Prompt
    # -----------------------------------------------------

    default_prompt_version: str = "v1"

    # -----------------------------------------------------
    # Dataset directories
    # -----------------------------------------------------

    datasets_dir: str = str(
        BASE_DIR / "app" / "datasets"
    )

    prompts_dir: str = str(
        BASE_DIR / "app" / "prompts"
    )

    # -----------------------------------------------------
    # Backward-compatible dataset directory
    # -----------------------------------------------------

    @property
    def dataset_dir(self) -> str:
        """
        Backward-compatible alias.

        Some Task23 files use:
            settings.dataset_dir

        Other files use:
            settings.datasets_dir
        """

        return self.datasets_dir

    # -----------------------------------------------------
    # Evaluation thresholds
    # -----------------------------------------------------

    relevance_threshold: float = 0.5

    groundedness_threshold: float = 0.5

    correctness_threshold: float = 0.5

    # -----------------------------------------------------
    # Pydantic configuration
    # -----------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


# =========================================================
# Global settings instance
# =========================================================

settings = Settings()