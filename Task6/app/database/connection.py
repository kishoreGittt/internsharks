import os

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()


MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "task6_auth_db")


if not MONGO_URI:
    raise ValueError("MONGO_URI is not configured in the .env file")


client = AsyncIOMotorClient(MONGO_URI)

database = client[DATABASE_NAME]

users_collection = database["users"]


async def connect_to_mongodb():
    """
    Connect to MongoDB and create a unique index
    on the email field.
    """

    await client.admin.command("ping")

    await users_collection.create_index(
        "email",
        unique=True
    )

    print("MongoDB connected successfully")


async def close_mongodb():
    """
    Close MongoDB connection.
    """

    client.close()

    print("MongoDB connection closed")