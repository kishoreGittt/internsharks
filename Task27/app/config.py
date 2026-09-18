from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent

ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):

    # ---------------------------------------------------------
    # Application
    # ---------------------------------------------------------

    APP_NAME: str = (
        "Task 27 - AI Knowledge & Operations Copilot"
    )

    DEBUG: bool = True

    # ---------------------------------------------------------
    # MongoDB
    # ---------------------------------------------------------

    MONGODB_URI: str

    MONGODB_DB: str = "Task27"

    # ---------------------------------------------------------
    # JWT
    # ---------------------------------------------------------

    JWT_SECRET: str

    JWT_ALGORITHM: str = "HS256"

    JWT_EXPIRE_MINUTES: int = 60

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ---------------------------------------------------------
    # OpenRouter
    # ---------------------------------------------------------

    OPENROUTER_API_KEY: str

    OPENROUTER_MODEL: str = (
        "openai/gpt-oss-20b:free"
    )

    OPENROUTER_VISION_MODEL: str = (
        "openai/gpt-4o-mini"
    )

    # ---------------------------------------------------------
    # RAG
    # ---------------------------------------------------------

    CHUNK_SIZE: int = 800

    CHUNK_OVERLAP: int = 100

    TOP_K: int = 3

    # ---------------------------------------------------------
    # File upload
    # ---------------------------------------------------------

    MAX_FILE_SIZE: int = 10485760

    UPLOAD_DIR: str = "data/uploads"

    VECTOR_DIR: str = "data/vector"

    # ---------------------------------------------------------
    # Conversation
    # ---------------------------------------------------------

    HISTORY_LIMIT: int = 10

    # Compatibility name used by other Task 27 files
    MAX_HISTORY_MESSAGES: int = 10

    # ---------------------------------------------------------
    # Tool calling
    # ---------------------------------------------------------

    MAX_TOOL_ROUNDS: int = 5

    # ---------------------------------------------------------
    # Embeddings
    # ---------------------------------------------------------

    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # ---------------------------------------------------------
    # Prompt / privacy
    # ---------------------------------------------------------

    PROMPT_VERSION: str = "v1"

    SENSITIVE_PROMPTS: bool = False

    # ---------------------------------------------------------
    # Pydantic settings configuration
    # ---------------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()