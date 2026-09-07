import os

from dotenv import load_dotenv

load_dotenv()


OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "google/gemma-4-26b-a4b-it:free"
)

OPENROUTER_FALLBACK_MODELS = [
    model.strip()
    for model in os.getenv(
        "OPENROUTER_FALLBACK_MODELS",
        "openrouter/free"
    ).split(";")
    if model.strip()
]

OPENROUTER_URL = os.getenv(
    "OPENROUTER_URL",
    "https://openrouter.ai/api/v1/chat/completions"
)

MAX_AGENT_STEPS = int(
    os.getenv("MAX_AGENT_STEPS", "10")
)