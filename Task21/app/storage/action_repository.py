from datetime import datetime, timezone

from app.database.mongodb import (
    agent_actions_collection,
    serialize_mongo_document,
)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


async def create_action(action_data: dict):
    action_data["created_at"] = utc_now()
    action_data["updated_at"] = utc_now()

    result = await agent_actions_collection.insert_one(action_data)

    created_action = await agent_actions_collection.find_one(
        {"_id": result.inserted_id}
    )

    return serialize_mongo_document(created_action)


async def get_action(action_id: str):
    action = await agent_actions_collection.find_one(
        {"action_id": action_id}
    )

    return serialize_mongo_document(action)


async def get_action_for_run(run_id: str, action_id: str):
    action = await agent_actions_collection.find_one(
        {
            "run_id": run_id,
            "action_id": action_id,
        }
    )

    return serialize_mongo_document(action)


async def update_action(action_id: str, update_data: dict):
    update_data["updated_at"] = utc_now()

    await agent_actions_collection.update_one(
        {"action_id": action_id},
        {"$set": update_data},
    )

    updated_action = await agent_actions_collection.find_one(
        {"action_id": action_id}
    )

    return serialize_mongo_document(updated_action)