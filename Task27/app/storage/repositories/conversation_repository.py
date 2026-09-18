from datetime import datetime, timezone
from typing import Optional

from app.storage.mongodb import conversations_collection


def utc_now():
    return datetime.now(timezone.utc)


async def create_conversation(
    user_id: str,
    conversation_id: str
):

    conversation = {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "messages": [],
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }

    await conversations_collection.insert_one(conversation)

    return conversation


async def get_conversation(
    user_id: str,
    conversation_id: str
) -> Optional[dict]:

    return await conversations_collection.find_one(
        {
            "user_id": user_id,
            "conversation_id": conversation_id,
        },
        {"_id": 0}
    )


async def add_message(
    user_id: str,
    conversation_id: str,
    role: str,
    content: str
):

    message = {
        "role": role,
        "content": content,
        "created_at": utc_now(),
    }

    await conversations_collection.update_one(
        {
            "user_id": user_id,
            "conversation_id": conversation_id,
        },
        {
            "$push": {
                "messages": message
            },
            "$set": {
                "updated_at": utc_now()
            }
        }
    )


async def get_recent_messages(
    user_id: str,
    conversation_id: str,
    limit: int = 10
):

    conversation = await get_conversation(
        user_id,
        conversation_id
    )

    if not conversation:
        return []

    messages = conversation.get("messages", [])

    return messages[-limit:]