from pymongo import MongoClient
from app.config import MONGO_URI, MONGO_DB

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
db = client[MONGO_DB]

runs_collection = db["runs"]
actions_collection = db["actions"]
projects_collection = db["projects"]
employees_collection = db["employees"]
tasks_collection = db["tasks"]
import os

from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()


MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb:mongodb+srv://kishorerajavel003_db_user:0kBzppKAJiTBcJMu@cluster0.wnmsgxj.mongodb.net/?appName=Cluster0",
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