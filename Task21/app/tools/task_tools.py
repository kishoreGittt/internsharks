from bson import ObjectId

from app.database.mongodb import (
    tasks_collection,
    projects_collection,
    employees_collection
)


async def get_project_tasks(project_id: str):

    tasks = []

    cursor = tasks_collection.find(
        {"project_id": project_id},
        {"_id": 0}
    )

    async for task in cursor:
        tasks.append(task)

    return tasks


async def get_task(task_id: str):

    task = await tasks_collection.find_one(
        {"task_id": task_id},
        {"_id": 0}
    )

    if not task:
        return {
            "found": False,
            "message": "Task not found"
        }

    return {
        "found": True,
        "task": task
    }


async def create_project_task(
    project_id: str,
    title: str,
    priority: str = "medium",
    assigned_to: str | None = None
):

    project = await projects_collection.find_one(
        {"project_id": project_id}
    )

    if not project:
        raise ValueError("Project not found")

    if priority not in [
        "low",
        "medium",
        "high"
    ]:
        raise ValueError(
            "Priority must be low, medium or high"
        )

    if assigned_to:

        employee = await employees_collection.find_one(
            {"employee_id": assigned_to}
        )

        if not employee:
            raise ValueError(
                "Assigned employee not found"
            )

    task_id = str(ObjectId())

    task = {
        "task_id": task_id,
        "project_id": project_id,
        "title": title,
        "priority": priority,
        "assigned_to": assigned_to,
        "status": "todo"
    }

    await tasks_collection.insert_one(task)

    return {
        "success": True,
        "task": task
    }


async def update_task_status(
    task_id: str,
    status: str
):

    allowed = [
        "todo",
        "in_progress",
        "completed"
    ]

    if status not in allowed:
        raise ValueError(
            "Invalid task status"
        )

    task = await tasks_collection.find_one(
        {"task_id": task_id}
    )

    if not task:
        raise ValueError(
            "Task not found"
        )

    await tasks_collection.update_one(
        {"task_id": task_id},
        {
            "$set": {
                "status": status
            }
        }
    )

    return {
        "success": True,
        "message": "Task status updated"
    }


async def delete_project_task(task_id: str):

    task = await tasks_collection.find_one(
        {"task_id": task_id}
    )

    if not task:
        raise ValueError(
            "Task not found"
        )

    await tasks_collection.delete_one(
        {"task_id": task_id}
    )

    return {
        "success": True,
        "message": "Task deleted"
    }