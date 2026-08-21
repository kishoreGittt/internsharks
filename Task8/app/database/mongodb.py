import os

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv


# Load .env
load_dotenv()


# Get MongoDB URI
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI is not found in .env file")


# Create MongoDB client
client = AsyncIOMotorClient(MONGO_URI)


# Database
database = client["task8_db"]


# Collection
users_collection = database["users"]


# Test MongoDB connection
async def connect_to_mongodb():

    try:
        await client.admin.command("ping")

        print("====================================")
        print("MongoDB connected successfully")
        print("Database: task8_db")
        print("====================================")

    except Exception as e:

        print("====================================")
        print("MongoDB connection failed")
        print("Error:", e)
        print("====================================")


# Close MongoDB connection
async def close_mongodb():

    client.close()

    print("MongoDB connection closed")