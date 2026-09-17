
import os

from dotenv import load_dotenv


load_dotenv()


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()

OPENROUTER_BASE_URL = os.getenv(
    "OPENROUTER_BASE_URL",
    "https://openrouter.ai/api/v1",
).rstrip("/")

OPENROUTER_VISION_MODEL = os.getenv(
    "OPENROUTER_VISION_MODEL",
    "inclusionai/ling-3.0-flash-vl:free",
).strip()

OPENROUTER_IMAGE_MODEL = os.getenv(
    "OPENROUTER_IMAGE_MODEL",
    "x-ai/grok-imagine-image-2.0",
).strip()

MAX_IMAGE_SIZE_MB = int(
    os.getenv("MAX_IMAGE_SIZE_MB", "10")
)

OPENROUTER_TIMEOUT_SECONDS = float(
    os.getenv("OPENROUTER_TIMEOUT_SECONDS", "120")
)

MAX_OUTPUT_RETRIES = int(
    os.getenv("MAX_OUTPUT_RETRIES", "1")
)

MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024