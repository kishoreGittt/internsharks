from app.database.mongodb import agent_actions_collection


async def create_action(action: dict):
    await agent_actions_collection.insert_one(action)
    return action


async def get_action(action_id: str):
    return await agent_actions_collection.find_one(
        {"action_id": action_id},
        {"_id": 0}
    )


async def update_action(action_id: str, updates: dict):
    await agent_actions_collection.update_one(
        {"action_id": action_id},
        {"$set": updates}
    )


async def get_action_for_run(run_id: str, action_id: str):
    return await agent_actions_collection.find_one(
        {
            "run_id": run_id,
            "action_id": action_id
        },
        {"_id": 0}
    )