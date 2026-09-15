from datetime import datetime, timezone
from app.storage.database import actions_collection

def execute_idempotently(run_id, action_id, tool_name, operation):
    key = f"{run_id}:{action_id}"
    existing = actions_collection.find_one({"idempotency_key": key})

    if existing and existing.get("status") == "executed":
        return existing["result"], True

    actions_collection.update_one(
        {"idempotency_key": key},
        {"$setOnInsert": {
            "run_id": run_id,
            "action_id": action_id,
            "tool": tool_name,
            "idempotency_key": key,
            "status": "started",
            "attempt_count": 0,
            "created_at": datetime.now(timezone.utc)
        }},
        upsert=True
    )

    result = operation()

    actions_collection.update_one(
        {"idempotency_key": key},
        {"$set": {
            "status": "executed",
            "result": result,
            "completed_at": datetime.now(timezone.utc)
        }}
    )
    return result, False
