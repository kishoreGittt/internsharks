import logging
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import HTTPException, status

from app.database.mongodb import tasks_collection, users_collection
from app.models.task import (
    TaskCreate,
    TaskStatusUpdate,
    TaskUpdate,
)


logger = logging.getLogger(__name__)


def serialize_task(task: dict) -> dict:

    return {
        "id": str(task["_id"]),
        "title": task["title"],
        "description": task["description"],
        "status": task["status"],
        "priority": task["priority"],
        "created_by": str(task["created_by"]),
        "assigned_to": (
            str(task["assigned_to"])
            if task.get("assigned_to")
            else None
        ),
        "due_date": task.get("due_date"),
        "created_at": task["created_at"],
        "updated_at": task["updated_at"],
    }


def validate_object_id(
    value: str,
    field_name: str
) -> ObjectId:

    if not ObjectId.is_valid(value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name}",
        )

    return ObjectId(value)


async def validate_assigned_user(
    assigned_to: str | None
):

    if assigned_to is None:
        return None

    user_id = validate_object_id(
        assigned_to,
        "assigned user ID"
    )

    user = await users_collection.find_one(
        {"_id": user_id}
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found",
        )

    return user_id


async def create_task(
    data: TaskCreate,
    current_user: dict
):

    assigned_to = await validate_assigned_user(
        data.assigned_to
    )

    now = datetime.now(timezone.utc)

    task = {
        "title": data.title,
        "description": data.description,
        "status": data.status,
        "priority": data.priority,
        "created_by": ObjectId(current_user["id"]),
        "assigned_to": assigned_to,
        "due_date": data.due_date,
        "created_at": now,
        "updated_at": now,
    }

    result = await tasks_collection.insert_one(task)

    task["_id"] = result.inserted_id

    logger.info(
        "Task created: task_id=%s user_id=%s",
        str(result.inserted_id),
        current_user["id"]
    )

    return serialize_task(task)


def user_can_access_task(
    task: dict,
    user_id: str
) -> bool:

    current_id = ObjectId(user_id)

    return (
        task["created_by"] == current_id
        or task.get("assigned_to") == current_id
    )


async def get_task(
    task_id: str,
    current_user: dict
):

    object_id = validate_object_id(
        task_id,
        "task ID"
    )

    task = await tasks_collection.find_one(
        {"_id": object_id}
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if current_user["role"] != "admin":
        if not user_can_access_task(
            task,
            current_user["id"]
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this task",
            )

    return serialize_task(task)


async def get_tasks(
    current_user: dict,
    page: int,
    limit: int,
    task_status: str | None = None,
    priority: str | None = None,
    assigned_to: str | None = None,
    search: str | None = None,
):

    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be greater than 0",
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 100",
        )

    query = {}

    if current_user["role"] != "admin":

        user_id = ObjectId(
            current_user["id"]
        )

        query["$or"] = [
            {"created_by": user_id},
            {"assigned_to": user_id},
        ]

    if task_status:
        query["status"] = task_status

    if priority:
        query["priority"] = priority

    if assigned_to:
        assigned_id = validate_object_id(
            assigned_to,
            "assigned user ID"
        )

        query["assigned_to"] = assigned_id

    if search:
        query["title"] = {
            "$regex": search,
            "$options": "i",
        }

    total = await tasks_collection.count_documents(
        query
    )

    skip = (page - 1) * limit

    cursor = (
        tasks_collection
        .find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    tasks = []

    async for task in cursor:
        tasks.append(
            serialize_task(task)
        )

    return {
        "success": True,
        "page": page,
        "limit": limit,
        "total": total,
        "data": tasks,
    }


async def update_task(
    task_id: str,
    data: TaskUpdate,
    current_user: dict
):

    object_id = validate_object_id(
        task_id,
        "task ID"
    )

    task = await tasks_collection.find_one(
        {"_id": object_id}
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if current_user["role"] != "admin":
        if task["created_by"] != ObjectId(
            current_user["id"]
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this task",
            )

    assigned_to = await validate_assigned_user(
        data.assigned_to
    )

    update_data = {
        "title": data.title,
        "description": data.description,
        "status": data.status,
        "priority": data.priority,
        "assigned_to": assigned_to,
        "due_date": data.due_date,
        "updated_at": datetime.now(timezone.utc),
    }

    await tasks_collection.update_one(
        {"_id": object_id},
        {"$set": update_data},
    )

    updated_task = await tasks_collection.find_one(
        {"_id": object_id}
    )

    logger.info(
        "Task updated: task_id=%s user_id=%s",
        task_id,
        current_user["id"]
    )

    return serialize_task(updated_task)


async def update_task_status(
    task_id: str,
    data: TaskStatusUpdate,
    current_user: dict
):

    object_id = validate_object_id(
        task_id,
        "task ID"
    )

    task = await tasks_collection.find_one(
        {"_id": object_id}
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if current_user["role"] != "admin":
        if not user_can_access_task(
            task,
            current_user["id"]
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this task",
            )

    await tasks_collection.update_one(
        {"_id": object_id},
        {
            "$set": {
                "status": data.status,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    updated_task = await tasks_collection.find_one(
        {"_id": object_id}
    )

    logger.info(
        "Task status updated: task_id=%s user_id=%s",
        task_id,
        current_user["id"]
    )

    return serialize_task(updated_task)


async def delete_task(
    task_id: str,
    current_user: dict
):

    object_id = validate_object_id(
        task_id,
        "task ID"
    )

    task = await tasks_collection.find_one(
        {"_id": object_id}
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if current_user["role"] != "admin":
        if task["created_by"] != ObjectId(
            current_user["id"]
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this task",
            )

    await tasks_collection.delete_one(
        {"_id": object_id}
    )

    logger.info(
        "Task deleted: task_id=%s user_id=%s",
        task_id,
        current_user["id"]
    )

    return {
        "success": True,
        "message": "Task deleted successfully",
    }


async def assign_task(
    task_id: str,
    user_id: str
):

    task_object_id = validate_object_id(
        task_id,
        "task ID"
    )

    user_object_id = validate_object_id(
        user_id,
        "user ID"
    )

    task = await tasks_collection.find_one(
        {"_id": task_object_id}
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    user = await users_collection.find_one(
        {"_id": user_object_id}
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found",
        )

    await tasks_collection.update_one(
        {"_id": task_object_id},
        {
            "$set": {
                "assigned_to": user_object_id,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    updated_task = await tasks_collection.find_one(
        {"_id": task_object_id}
    )

    return serialize_task(updated_task)