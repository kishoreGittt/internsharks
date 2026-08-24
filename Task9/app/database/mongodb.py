from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings


client = AsyncIOMotorClient(settings.MONGO_URI)

database = client[settings.DATABASE_NAME]

users_collection = database["users"]
refresh_sessions_collection = database["refresh_sessions"]


async def connect_to_mongodb():
    try:
        await client.admin.command("ping")
        print("MongoDB connected successfully")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        raise


async def close_mongodb():
    client.close()
    print("MongoDB connection closed")


async def create_indexes():
    await users_collection.create_index(
        "email",
        unique=True
    )

    await refresh_sessions_collection.create_index(
        "jti_hash",
        unique=True
    )

    await refresh_sessions_collection.create_index(
        "user_id"
    )