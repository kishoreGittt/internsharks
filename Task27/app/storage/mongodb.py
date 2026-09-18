from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError

from app.config import settings


# =========================================================
# MONGODB CLIENT
# =========================================================

client = AsyncIOMotorClient(
    settings.MONGODB_URI,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000,
    socketTimeoutMS=5000
)


# =========================================================
# DATABASE
# =========================================================

db = client[settings.MONGODB_DB]


# =========================================================
# COLLECTIONS
# =========================================================

users_collection = db["users"]

documents_collection = db["documents"]

chunks_collection = db["chunks"]

jobs_collection = db["jobs"]

conversations_collection = db["conversations"]

projects_collection = db["projects"]

traces_collection = db["traces"]


# =========================================================
# CREATE INDEXES
# =========================================================

async def create_indexes():

    # USERS
    await users_collection.create_index(
        "email",
        unique=True
    )

    # DOCUMENTS
    await documents_collection.create_index(
        [
            ("user_id", 1),
            ("document_id", 1)
        ],
        unique=True
    )

    await documents_collection.create_index(
        [
            ("user_id", 1),
            ("content_hash", 1)
        ]
    )

    # CHUNKS
    await chunks_collection.create_index(
        [
            ("user_id", 1),
            ("document_id", 1)
        ]
    )

    # JOBS
    await jobs_collection.create_index(
        [
            ("status", 1),
            ("created_at", 1)
        ]
    )

    await jobs_collection.create_index(
        [
            ("user_id", 1),
            ("job_id", 1)
        ],
        unique=True
    )

    # CONVERSATIONS
    await conversations_collection.create_index(
        [
            ("user_id", 1),
            ("conversation_id", 1)
        ],
        unique=True
    )

    # PROJECTS
    await projects_collection.create_index(
        [
            ("user_id", 1),
            ("project_id", 1)
        ],
        unique=True
    )

    # TRACES
    await traces_collection.create_index(
        [
            ("user_id", 1),
            ("trace_id", 1)
        ],
        unique=True
    )

    print("MongoDB indexes created successfully.")


# =========================================================
# MONGODB HEALTH CHECK
# =========================================================

async def ping_mongodb():

    try:

        await client.admin.command("ping")

        return True

    except ServerSelectionTimeoutError:

        return False

    except Exception:

        return False


# =========================================================
# GET DATABASE STATUS
# =========================================================

async def get_mongodb_status():

    try:

        await client.admin.command("ping")

        return {
            "status": "healthy",
            "database": settings.MONGODB_DB
        }

    except Exception as exc:

        return {
            "status": "unhealthy",
            "database": settings.MONGODB_DB,
            "error": str(exc)
        }


# =========================================================
# CLOSE CONNECTION
# =========================================================

async def close_mongodb():

    client.close()

    print("MongoDB connection closed.")