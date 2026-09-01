from app.config import MAX_HISTORY_MESSAGES
from app.prompts.chat_prompt import SYSTEM_PROMPT

from app.services.ai_service import generate_chat_response

from app.storage.chat_memory import (
    add_message,
    clear_session,
    create_session,
    get_history,
    session_exists
)


async def chat_with_ai(
    session_id: str,
    user_message: str
) -> str:

    # Create session if it does not exist
    if not session_exists(session_id):
        create_session(session_id)

    # Get previous conversation
    history = get_history(session_id)

    # Keep only the last 10 messages
    recent_history = history[-MAX_HISTORY_MESSAGES:]

    # Build messages for OpenRouter
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    messages.extend(recent_history)

    # Add the current user message
    messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    # Send conversation to OpenRouter
    ai_response = await generate_chat_response(messages)

    # Store user message
    add_message(
        session_id=session_id,
        role="user",
        content=user_message
    )

    # Store assistant response
    add_message(
        session_id=session_id,
        role="assistant",
        content=ai_response
    )

    return ai_response


def get_chat_history(session_id: str) -> list[dict]:

    if not session_exists(session_id):
        raise ValueError("Chat session not found")

    return get_history(session_id)


def delete_chat_session(session_id: str) -> None:

    if not session_exists(session_id):
        raise ValueError("Chat session not found")

    clear_session(session_id)