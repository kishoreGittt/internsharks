from motor.motor_asyncio import AsyncIOMotorClient

from app.config import MONGO_URI, DATABASE_NAME


# ============================================================
# MongoDB Client
# ============================================================

client = AsyncIOMotorClient(MONGO_URI)

database = client[DATABASE_NAME]

users_collection = database["users"]


# ============================================================
# Database Connection
# ============================================================

async def connect_to_mongodb():

    try:

        await client.admin.command("ping")

        print("MongoDB connected successfully")

    except Exception as e:

        print("MongoDB connection failed")

        raise RuntimeError(
            "Unable to connect to MongoDB"
        )


# ============================================================
# Database Disconnection
# ============================================================

async def close_mongodb_connection():

    client.close()

    print("MongoDB connection closed")