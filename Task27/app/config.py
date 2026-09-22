from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # =====================================================
    # APPLICATION
    # =====================================================

    APP_NAME: str = "Task 27 AI Knowledge & Operations Copilot"

    DEBUG: bool = True

    # =====================================================
    # MONGODB
    # =====================================================



    MONGODB_URI: str

    MONGODB_DB: str = "task27"

    # =====================================================
    # JWT
    # =====================================================

    JWT_SECRET: str

    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # =====================================================
    # OPENROUTER
    # =====================================================

    OPENROUTER_API_KEY: str

    OPENROUTER_BASE_URL: str = (
        "https://openrouter.ai/api/v1"
    )

    OPENROUTER_MODEL: str = (
        "openai/gpt-oss-20b:free"
    )

    OPENROUTER_VISION_MODEL: str = (
        "google/gemini-2.0-flash-exp:free"
    )

    OPENROUTER_TIMEOUT_SECONDS: int = 120

    # =====================================================
    # FILE / RAG
    # =====================================================

    UPLOAD_DIR: str = "data/documents"

    VECTOR_DIR: str = "vector_data"

    MAX_FILE_SIZE: int = 10 * 1024 * 1024

    CHUNK_SIZE: int = 800

    CHUNK_OVERLAP: int = 100

    TOP_K: int = 3
    


    # =====================================================
    # CONVERSATION
    # =====================================================

    MAX_HISTORY_MESSAGES: int = 10

    MAX_TOOL_ROUNDS: int = 10

    # =====================================================
    # RED TEAM
    # =====================================================

    RED_TEAM_ENABLED: bool = True

    RED_TEAM_ALLOW_SIMULATION: bool = True

    SIMULATE_OPENROUTER_FAILURE: bool = False

    SIMULATE_OPENROUTER_TIMEOUT: bool = False

    SIMULATE_MALFORMED_AI_OUTPUT: bool = False

    SIMULATE_TOOL_FAILURE: bool = False

    # =====================================================
    # PYDANTIC SETTINGS
    # =====================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()