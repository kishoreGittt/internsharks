from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


client = AsyncIOMotorClient(settings.MONGO_URI)

database = client[settings.DATABASE_NAME]

users_collection = database["users"]
refresh_sessions_collection = database["refresh_sessions"]


async def connect_database():
    try:
        await client.admin.command("ping")
        print("MongoDB connected successfully")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        raise


async def close_database():
    client.close()
    print("MongoDB connection closed")