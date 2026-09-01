from typing import Dict, List


chat_memory: Dict[str, List[dict]] = {}


def session_exists(session_id: str) -> bool:
    return session_id in chat_memory


def create_session(session_id: str) -> None:
    if session_id not in chat_memory:
        chat_memory[session_id] = []


def get_history(session_id: str) -> List[dict]:
    return chat_memory.get(session_id, [])


def add_message(
    session_id: str,
    role: str,
    content: str
) -> None:

    if session_id not in chat_memory:
        chat_memory[session_id] = []

    chat_memory[session_id].append(
        {
            "role": role,
            "content": content
        }
    )


def clear_session(session_id: str) -> None:
    if session_id in chat_memory:
        del chat_memory[session_id]