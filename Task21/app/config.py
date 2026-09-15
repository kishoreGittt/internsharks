import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://kishorerajavel003_db_user:0kBzppKAJiTBcJMu@cluster0.wnmsgxj.mongodb.net/?appName=Cluster0"
)

MONGO_DB = os.getenv(
    "MONGO_DB",
    "task21_db"
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL")

OPENROUTER_URL = os.getenv(
    "OPENROUTER_URL",
    "https://openrouter.ai/api/v1/chat/completions"
)

MAX_AGENT_STEPS = int(
    os.getenv("MAX_AGENT_STEPS", "10")
)