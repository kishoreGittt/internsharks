"""
MongoDB Atlas connection for Task24.
"""

from typing import Optional

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
)

from app.config import (
    MONGODB_DATABASE,
    MONGODB_URI,
)


mongodb_client: Optional[AsyncIOMotorClient] = None
mongodb_database: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongodb() -> None:
    """
    Connect to MongoDB Atlas when FastAPI starts.
    """

    global mongodb_client
    global mongodb_database

    if not MONGODB_URI:
        print(
            "WARNING: MONGODB_URI is not configured. "
            "MongoDB features may not work."
        )
        return

    try:
        mongodb_client = AsyncIOMotorClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,
        )

        # Verify the connection.
        await mongodb_client.admin.command("ping")

        mongodb_database = mongodb_client[
            MONGODB_DATABASE
        ]

        print(
            f"Connected to MongoDB database: "
            f"{MONGODB_DATABASE}"
        )

    except Exception as exc:
        mongodb_client = None
        mongodb_database = None

        print(
            f"WARNING: MongoDB connection failed: {exc}"
        )


async def close_mongodb_connection() -> None:
    """
    Close MongoDB connection when FastAPI stops.
    """

    global mongodb_client
    global mongodb_database

    if mongodb_client is not None:
        mongodb_client.close()

        mongodb_client = None
        mongodb_database = None

        print("MongoDB connection closed.")


def get_database() -> AsyncIOMotorDatabase:
    """
    Return the connected MongoDB database.

    Raises:
        RuntimeError: If MongoDB is not connected.
    """

    if mongodb_database is None:
        raise RuntimeError(
            "MongoDB is not connected. "
            "Check your MONGODB_URI in the .env file."
        )

    return mongodb_database