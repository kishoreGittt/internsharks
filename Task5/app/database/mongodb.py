from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os


# ============================================================
# Load Environment Variables
# ============================================================

load_dotenv()


# ============================================================
# MongoDB Configuration
# ============================================================

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "student_management")


if not MONGO_URI:
    raise ValueError(
        "MONGO_URI is not configured in the .env file"
    )


# ============================================================
# MongoDB Client
# ============================================================

client = AsyncIOMotorClient(MONGO_URI)


# ============================================================
# Database
# ============================================================

database = client[DATABASE_NAME]


# ============================================================
# Students Collection
# ============================================================

student_collection = database["students"]