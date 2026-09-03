tasks = {
    1: {
        "id": 1,
        "title": "Complete authentication API",
        "status": "completed"
    },
    2: {
        "id": 2,
        "title": "Implement RAG",
        "status": "in_progress"
    },
    3: {
        "id": 3,
        "title": "Build AI summarization API",
        "status": "completed"
    },
    4: {
        "id": 4,
        "title": "Implement AI tool calling",
        "status": "todo"
    }
}


def get_task(task_id: int) -> dict:
    """
    Find a task by its ID.
    """

    task = tasks.get(task_id)

    if task is None:
        return {
            "found": False,
            "message": f"Task {task_id} was not found."
        }

    return {
        "found": True,
        "task": task
    }