from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.config import settings
from app.storage.mongodb import conversations_collection


def utc_now():
    return datetime.now(timezone.utc)


# =========================================================
# CREATE CONVERSATION
# =========================================================

async def create_conversation(
    conversation_id: str,
    user_id: str,
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

    await conversations_collection.insert_one(
        conversation
    )

    conversation.pop("_id", None)

    return conversation


# =========================================================
# GET OR CREATE CONVERSATION
# =========================================================

async def get_or_create_conversation(
    conversation_id: Optional[str],
    user_id: str,
):
    """
    Get an existing conversation belonging to the user.

    If conversation_id does not exist, create a new one.

    IMPORTANT:
    Argument order matches chat.py:

        get_or_create_conversation(
            conversation_id,
            owner_id
        )
    """

    if conversation_id:

        conversation = await get_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
        )

        if conversation:
            return conversation

        # Do not silently create a different user's
        # conversation when an explicit ID was supplied.
        #
        # For a supplied ID that doesn't belong to this
        # user, create a new conversation using that ID
        # only if it does not exist at all.

        existing_any_user = (
            await conversations_collection.find_one(
                {
                    "conversation_id":
                        conversation_id
                },
                {
                    "_id": 1,
                    "user_id": 1
                }
            )
        )

        if existing_any_user:
            return None

    new_conversation_id = (
        conversation_id
        if conversation_id
        else f"conv_{uuid4().hex}"
    )

    return await create_conversation(
        conversation_id=new_conversation_id,
        user_id=user_id,
    )


# =========================================================
# GET CONVERSATION
# =========================================================

async def get_conversation(
    conversation_id: str,
    user_id: str,
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


# =========================================================
# ADD MESSAGE
# =========================================================

async def add_message(
    conversation_id: str,
    user_id: str,
    role: str,
    content: str,
):
    """
    Add one message to a conversation.

    Argument order matches chat.py:
        conversation_id,
        owner_id,
        content
    """

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


# =========================================================
# SAVE USER MESSAGE
# =========================================================

async def save_user_message(
    conversation_id: str,
    user_id: str,
    content: str,
):
    return await add_message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="user",
        content=content,
    )


# =========================================================
# SAVE ASSISTANT MESSAGE
# =========================================================

async def save_assistant_message(
    conversation_id: str,
    user_id: str,
    content: str,
):
    return await add_message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="assistant",
        content=content,
    )


# =========================================================
# GET HISTORY
# =========================================================

async def get_history(
    conversation_id: str,
    user_id: str,
    limit: Optional[int] = None,
):
    conversation = await get_conversation(
        conversation_id=conversation_id,
        user_id=user_id,
    )

    if not conversation:
        return []

    messages = conversation.get(
        "messages",
        []
    )

    # Prevent Settings AttributeError
    if limit is None:
        limit = getattr(
            settings,
            "MAX_HISTORY_MESSAGES",
            20
        )

    # Safety check
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = 20

    if limit <= 0:
        limit = 20

    return messages[-limit:]


# =========================================================
# GET CONVERSATION HISTORY
# =========================================================

async def get_conversation_history(
    conversation_id: str,
    user_id: str,
    limit: Optional[int] = None,
):
    return await get_history(
        conversation_id=conversation_id,
        user_id=user_id,
        limit=limit,
    )


# =========================================================
# HISTORY
# =========================================================

async def history(
    conversation_id: str,
    user_id: str,
    limit: Optional[int] = None,
):
    """
    Compatibility wrapper used by chat.py.
    """

    return await get_history(
        conversation_id=conversation_id,
        user_id=user_id,
        limit=limit,
    )


# =========================================================
# DELETE CONVERSATION
# =========================================================

async def delete_conversation(
    conversation_id: str,
    user_id: str,
):
    result = await conversations_collection.delete_one(
        {
            "user_id": user_id,
            "conversation_id": conversation_id,
        }
    )

    return result.deleted_count > 0