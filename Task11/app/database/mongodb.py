import logging

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings


logger = logging.getLogger(__name__)


client = AsyncIOMotorClient(
    settings.MONGO_URI,
    serverSelectionTimeoutMS=5000,
)

database = client[settings.DATABASE_NAME]

users_collection = database["users"]
tasks_collection = database["tasks"]
refresh_tokens_collection = database["refresh_tokens"]


async def connect_to_database() -> None:
    try:
        await client.admin.command("ping")

        logger.info(
            "MongoDB connection established successfully"
        )

    except Exception:
        logger.exception(
            "MongoDB connection failed"
        )

        raise


async def close_database_connection() -> None:
    client.close()

    logger.info(
        "MongoDB connection closed"
    )


async def check_database_connection() -> bool:
    try:
        await client.admin.command("ping")
        return True

    except Exception:
        logger.warning(
            "MongoDB health check failed"
        )

        return False