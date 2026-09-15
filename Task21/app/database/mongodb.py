from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI, MONGO_DB


client = AsyncIOMotorClient(MONGO_URI)

db = client[MONGO_DB]

employees_collection = db["employees"]
projects_collection = db["projects"]
tasks_collection = db["tasks"]

agent_runs_collection = db["agent_runs"]
agent_actions_collection = db["agent_actions"]