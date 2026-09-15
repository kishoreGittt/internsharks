from pymongo import MongoClient
from app.config import MONGO_URI, MONGO_DB

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
db = client[MONGO_DB]

runs_collection = db["runs"]
actions_collection = db["actions"]
projects_collection = db["projects"]
employees_collection = db["employees"]
tasks_collection = db["tasks"]
