conversation_memory = {}


def get_history(session_id: str):

    return conversation_memory.get(
        session_id,
        []
    )


def add_message(session_id: str, message: dict):

    if session_id not in conversation_memory:
        conversation_memory[session_id] = []

    conversation_memory[session_id].append(message)


def clear_history(session_id: str):

    conversation_memory.pop(
        session_id,
        None
    )