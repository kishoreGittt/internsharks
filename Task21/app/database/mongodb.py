from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI, MONGO_DB


client = AsyncIOMotorClient(MONGO_URI)

database = client[MONGO_DB]

employees_collection = database["employees"]
projects_collection = database["projects"]
tasks_collection = database["tasks"]

agent_runs_collection = database["agent_runs"]
agent_actions_collection = database["agent_actions"]


def serialize_mongo_document(document):
    """
    Convert MongoDB ObjectId into a JSON-safe string.
    """

    if document is None:
        return None

    document["_id"] = str(document["_id"])

    return document