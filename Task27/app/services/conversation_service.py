from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.config import settings
from app.storage.mongodb import conversations_collection


def utc_now():
    return datetime.now(timezone.utc)


async def create_conversation(
    user_id: str,
    conversation_id: str,
    title: str = "New Conversation",
):
    conversation = {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "title": title,
        "messages": [],
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }

    await conversations_collection.insert_one(conversation)

    conversation.pop("_id", None)
    return conversation


async def get_or_create_conversation(
    user_id: str,
    conversation_id: Optional[str] = None,
):
    if conversation_id:
        conversation = await get_conversation(
            user_id=user_id,
            conversation_id=conversation_id,
        )

        if conversation:
            return conversation

    new_conversation_id = conversation_id or f"conv_{uuid4().hex}"

    return await create_conversation(
        user_id=user_id,
        conversation_id=new_conversation_id,
    )


async def get_conversation(
    user_id: str,
    conversation_id: str,
) -> Optional[dict]:
    return await conversations_collection.find_one(
        {
            "user_id": user_id,
            "conversation_id": conversation_id,
        },
        {
            "_id": 0
        },
    )


async def add_message(
    user_id: str,
    conversation_id: str,
    role: str,
    content: str,
):
    message = {
        "role": role,
        "content": content,
        "created_at": utc_now(),
    }

    result = await conversations_collection.update_one(
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
            },
        },
    )

    if result.matched_count == 0:
        return None

    return message


async def save_user_message(
    user_id: str,
    conversation_id: str,
    content: str,
):
    return await add_message(
        user_id=user_id,
        conversation_id=conversation_id,
        role="user",
        content=content,
    )


async def save_assistant_message(
    user_id: str,
    conversation_id: str,
    content: str,
):
    return await add_message(
        user_id=user_id,
        conversation_id=conversation_id,
        role="assistant",
        content=content,
    )


async def get_history(
    user_id: str,
    conversation_id: str,
    limit: Optional[int] = None,
):
    conversation = await get_conversation(
        user_id=user_id,
        conversation_id=conversation_id,
    )

    if not conversation:
        return []

    messages = conversation.get("messages", [])

    if limit is None:
        limit = settings.MAX_HISTORY_MESSAGES

    return messages[-limit:]


async def get_conversation_history(
    user_id: str,
    conversation_id: str,
    limit: Optional[int] = None,
):
    return await get_history(
        user_id=user_id,
        conversation_id=conversation_id,
        limit=limit,
    )


async def history(
    user_id: str,
    conversation_id: str,
    limit: Optional[int] = None,
):
    """
    Compatibility wrapper used by chat.py.
    Returns the latest conversation messages.
    """
    return await get_history(
        user_id=user_id,
        conversation_id=conversation_id,
        limit=limit,
    )


async def delete_conversation(
    user_id: str,
    conversation_id: str,
):
    result = await conversations_collection.delete_one(
        {
            "user_id": user_id,
            "conversation_id": conversation_id,
        }
    )

    return result.deleted_count > 0