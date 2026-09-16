import os

from dotenv import load_dotenv


load_dotenv()


APP_NAME = os.getenv(
    "APP_NAME",
    "Task24 AI Observability API",
).strip()


APP_VERSION = os.getenv(
    "APP_VERSION",
    "1.0.0",
).strip()


OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
    "",
).strip()


OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openai/gpt-oss-20b:free",
).strip()


MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "",
).strip()


MONGODB_DATABASE = os.getenv(
    "MONGODB_DATABASE",
    "task24_db",
).strip()


LOG_AI_CONTENT = os.getenv(
    "LOG_AI_CONTENT",
    "false",
).lower() == "true"