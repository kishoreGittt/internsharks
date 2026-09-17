import os

from dotenv import load_dotenv


load_dotenv()


MONGODB_URI = os.getenv("MONGODB_URI", "")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "task24_db")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "inclusionai/ling-3.0-flash-vl:free",
)

APP_NAME = os.getenv(
    "APP_NAME",
    "Task24 AI Observability",
)

PROMPT_VERSION = os.getenv(
    "PROMPT_VERSION",
    "assistant_v1",
)

LOG_AI_CONTENT = (
    os.getenv("LOG_AI_CONTENT", "false").strip().lower()
    in {"true", "1", "yes", "on"}
)

SLOW_REQUEST_THRESHOLD_MS = int(
    os.getenv("SLOW_REQUEST_THRESHOLD_MS", "3000")
)

OPENROUTER_TIMEOUT_SECONDS = int(
    os.getenv("OPENROUTER_TIMEOUT_SECONDS", "60")
)

MODEL_INPUT_PRICE_PER_MILLION = float(
    os.getenv("MODEL_INPUT_PRICE_PER_MILLION", "0.50")
)

MODEL_OUTPUT_PRICE_PER_MILLION = float(
    os.getenv("MODEL_OUTPUT_PRICE_PER_MILLION", "1.50")
)