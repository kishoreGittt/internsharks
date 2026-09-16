import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Task 23 - LLM Evaluation")
    database_path: str = os.getenv("DATABASE_PATH", "data/evaluations.db")
    dataset_dir: str = os.getenv("DATASET_DIR", "app/datasets")
    openrouter_api_key: str | None = os.getenv("OPENROUTER_API_KEY")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free")
    judge_enabled: bool = os.getenv("JUDGE_ENABLED", "false").lower() == "true"
    judge_model: str = os.getenv("JUDGE_MODEL", "openai/gpt-oss-20b:free")
    request_timeout_seconds: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "45"))
    min_relevance_score: float = float(os.getenv("MIN_RELEVANCE_SCORE", "0.8"))
    min_groundedness_score: float = float(os.getenv("MIN_GROUNDEDNESS_SCORE", "0.9"))
    min_correctness_score: float = float(os.getenv("MIN_CORRECTNESS_SCORE", "0.8"))

settings = Settings()

MODEL_PRICING = {
    # Add real provider pricing here when available.
    # Values are USD per one million tokens.
    "openai/gpt-oss-20b:free": {
        "input_cost_per_million_tokens": 0.0,
        "output_cost_per_million_tokens": 0.0,
    }
}
