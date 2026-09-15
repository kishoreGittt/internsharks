import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "task22_db")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_BASE_DELAY = float(os.getenv("RETRY_BASE_DELAY", "1"))
EXTERNAL_TOOL_TIMEOUT = float(os.getenv("EXTERNAL_TOOL_TIMEOUT", "5"))
OPENROUTER_TIMEOUT = float(os.getenv("OPENROUTER_TIMEOUT", "30"))
ENABLE_JITTER = os.getenv("ENABLE_JITTER", "false").lower() == "true"
