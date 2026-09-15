import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://localhost:27017",
)

MONGO_DATABASE = os.getenv(
    "MONGO_DATABASE",
    "task22_db",
)


client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000,
)

database = client[MONGO_DATABASE]


def check_database_connection():
    client.admin.command("ping")
    return True