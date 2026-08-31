import os

from dotenv import load_dotenv


load_dotenv()


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "openai/gpt-4o-mini"
)

# Maximum upload size = 5 MB
MAX_FILE_SIZE = 5 * 1024 * 1024