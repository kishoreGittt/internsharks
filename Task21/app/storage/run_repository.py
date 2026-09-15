from app.database.mongodb import agent_runs_collection


async def create_run(run_data: dict):
    await agent_runs_collection.insert_one(run_data)
    return run_data


async def get_run(run_id: str):
    return await agent_runs_collection.find_one(
        {"run_id": run_id},
        {"_id": 0}
    )


async def update_run(run_id: str, updates: dict):
    await agent_runs_collection.update_one(
        {"run_id": run_id},
        {"$set": updates}
    )


async def append_trace(run_id: str, event: dict):
    await agent_runs_collection.update_one(
        {"run_id": run_id},
        {"$push": {"execution_trace": event}}
    )


async def increment_step(run_id: str):
    await agent_runs_collection.update_one(
        {"run_id": run_id},
        {"$inc": {"step_count": 1}}
    )