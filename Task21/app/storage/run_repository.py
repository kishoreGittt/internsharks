from datetime import datetime, timezone

from app.database.mongodb import (
    agent_runs_collection,
    serialize_mongo_document,
)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


async def create_run(run_data: dict):
    run_data["created_at"] = utc_now()
    run_data["updated_at"] = utc_now()

    result = await agent_runs_collection.insert_one(run_data)

    created_run = await agent_runs_collection.find_one(
        {"_id": result.inserted_id}
    )

    return serialize_mongo_document(created_run)


async def get_run(run_id: str):
    run = await agent_runs_collection.find_one(
        {"run_id": run_id}
    )

    return serialize_mongo_document(run)


async def update_run(run_id: str, update_data: dict):
    update_data["updated_at"] = utc_now()

    await agent_runs_collection.update_one(
        {"run_id": run_id},
        {"$set": update_data},
    )

    updated_run = await agent_runs_collection.find_one(
        {"run_id": run_id}
    )

    return serialize_mongo_document(updated_run)


async def append_trace(run_id: str, trace_item: dict):
    trace_item["timestamp"] = utc_now()

    await agent_runs_collection.update_one(
        {"run_id": run_id},
        {
            "$push": {
                "execution_trace": trace_item
            },
            "$set": {
                "updated_at": utc_now()
            }
        },
    )


async def increment_step(run_id: str):
    await agent_runs_collection.update_one(
        {"run_id": run_id},
        {
            "$inc": {
                "step_count": 1
            },
            "$set": {
                "updated_at": utc_now()
            }
        },
    )