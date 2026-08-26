from datetime import datetime, timezone

from bson import ObjectId
from fastapi import HTTPException

from app.database.mongodb import (
    tasks_collection,
    users_collection
)


def validate_object_id(
    value: str,
    field_name: str
):

    if not ObjectId.is_valid(value):

        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error_code": 400,
                "message": f"Invalid {field_name}"
            }
        )

    return ObjectId(value)


def serialize_task(task):

    task["id"] = str(task["_id"])

    del task["_id"]

    task["created_by"] = str(
        task["created_by"]
    )

    if task.get("assigned_to"):

        task["assigned_to"] = str(
            task["assigned_to"]
        )

    return task


async def check_assigned_user(
    assigned_to: str | None
):

    if assigned_to is None:

        return None

    assigned_object_id = validate_object_id(
        assigned_to,
        "assigned user ID"
    )

    user = await users_collection.find_one(
        {
            "_id": assigned_object_id,
            "is_active": True
        }
    )

    if user is None:

        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error_code": 404,
                "message": "Assigned user not found"
            }
        )

    return assigned_object_id


async def create_task(
    data,
    current_user
):

    assigned_to = await check_assigned_user(
        data.assigned_to
    )

    now = datetime.now(timezone.utc)

    task_document = {
        "title": data.title.strip(),
        "description": data.description.strip(),
        "status": data.status.value,
        "priority": data.priority.value,
        "created_by": ObjectId(current_user["id"]),
        "assigned_to": assigned_to,
        "due_date": data.due_date,
        "created_at": now,
        "updated_at": now
    }

    result = await tasks_collection.insert_one(
        task_document
    )

    task = await tasks_collection.find_one(
        {
            "_id": result.inserted_id
        }
    )

    return serialize_task(task)


async def get_task_by_id(
    task_id: str,
    current_user
):

    task_object_id = validate_object_id(
        task_id,
        "task ID"
    )

    task = await tasks_collection.find_one(
        {
            "_id": task_object_id
        }
    )

    if task is None:

        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error_code": 404,
                "message": "Task not found"
            }
        )

    is_admin = current_user["role"] == "admin"

    is_owner = (
        str(task["created_by"])
        == current_user["id"]
    )

    is_assigned = (
        task.get("assigned_to")
        and str(task["assigned_to"])
        == current_user["id"]
    )

    if not (
        is_admin
        or is_owner
        or is_assigned
    ):

        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "error_code": 403,
                "message": "You are not allowed to access this task"
            }
        )

    return serialize_task(task)


async def update_task(
    task_id: str,
    data,
    current_user
):

    task_object_id = validate_object_id(
        task_id,
        "task ID"
    )

    task = await tasks_collection.find_one(
        {
            "_id": task_object_id
        }
    )

    if task is None:

        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error_code": 404,
                "message": "Task not found"
            }
        )

    is_admin = current_user["role"] == "admin"

    is_owner = (
        str(task["created_by"])
        == current_user["id"]
    )

    if not (is_admin or is_owner):

        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "error_code": 403,
                "message": "You are not allowed to update this task"
            }
        )

    assigned_to = await check_assigned_user(
        data.assigned_to
    )

    await tasks_collection.update_one(
        {
            "_id": task_object_id
        },
        {
            "$set": {
                "title": data.title.strip(),
                "description": data.description.strip(),
                "status": data.status.value,
                "priority": data.priority.value,
                "assigned_to": assigned_to,
                "due_date": data.due_date,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )

    updated_task = await tasks_collection.find_one(
        {
            "_id": task_object_id
        }
    )

    return serialize_task(updated_task)


async def update_task_status(
    task_id: str,
    data,
    current_user
):

    task_object_id = validate_object_id(
        task_id,
        "task ID"
    )

    task = await tasks_collection.find_one(
        {
            "_id": task_object_id
        }
    )

    if task is None:

        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error_code": 404,
                "message": "Task not found"
            }
        )

    is_admin = current_user["role"] == "admin"

    is_owner = (
        str(task["created_by"])
        == current_user["id"]
    )

    is_assigned = (
        task.get("assigned_to")
        and str(task["assigned_to"])
        == current_user["id"]
    )

    if not (
        is_admin
        or is_owner
        or is_assigned
    ):

        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "error_code": 403,
                "message": "You are not allowed to update this task"
            }
        )

    await tasks_collection.update_one(
        {
            "_id": task_object_id
        },
        {
            "$set": {
                "status": data.status.value,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )

    updated_task = await tasks_collection.find_one(
        {
            "_id": task_object_id
        }
    )

    return serialize_task(updated_task)


async def delete_task(
    task_id: str,
    current_user
):

    task_object_id = validate_object_id(
        task_id,
        "task ID"
    )

    task = await tasks_collection.find_one(
        {
            "_id": task_object_id
        }
    )

    if task is None:

        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error_code": 404,
                "message": "Task not found"
            }
        )

    is_admin = current_user["role"] == "admin"

    is_owner = (
        str(task["created_by"])
        == current_user["id"]
    )

    if not (is_admin or is_owner):

        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "error_code": 403,
                "message": "You are not allowed to delete this task"
            }
        )

    await tasks_collection.delete_one(
        {
            "_id": task_object_id
        }
    )

    return True


async def get_user_tasks(
    current_user,
    page: int,
    limit: int,
    status_filter=None,
    priority_filter=None,
    assigned_to=None,
    search=None
):

    if page < 1:

        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error_code": 400,
                "message": "Page must be greater than or equal to 1"
            }
        )

    if limit < 1 or limit > 100:

        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error_code": 400,
                "message": "Limit must be between 1 and 100"
            }
        )

    if current_user["role"] == "admin":

        query = {}

    else:

        user_object_id = ObjectId(
            current_user["id"]
        )

        query = {
            "$or": [
                {
                    "created_by": user_object_id
                },
                {
                    "assigned_to": user_object_id
                }
            ]
        }

    if status_filter:

        query["status"] = status_filter.value

    if priority_filter:

        query["priority"] = priority_filter.value

    if assigned_to:

        assigned_object_id = validate_object_id(
            assigned_to,
            "assigned user ID"
        )

        if current_user["role"] != "admin":

            user_object_id = ObjectId(
                current_user["id"]
            )

            query = {
                "$and": [
                    {
                        "$or": [
                            {
                                "created_by": user_object_id
                            },
                            {
                                "assigned_to": user_object_id
                            }
                        ]
                    },
                    {
                        "assigned_to": assigned_object_id
                    }
                ]
            }

        else:

            query["assigned_to"] = assigned_object_id

    if search:

        query["title"] = {
            "$regex": search.strip(),
            "$options": "i"
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
        "data": tasks
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
        {
            "_id": task_object_id
        }
    )

    if task is None:

        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error_code": 404,
                "message": "Task not found"
            }
        )

    user = await users_collection.find_one(
        {
            "_id": user_object_id,
            "is_active": True
        }
    )

    if user is None:

        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error_code": 404,
                "message": "Assigned user not found"
            }
        )

    await tasks_collection.update_one(
        {
            "_id": task_object_id
        },
        {
            "$set": {
                "assigned_to": user_object_id,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )

    updated_task = await tasks_collection.find_one(
        {
            "_id": task_object_id
        }
    )

    return serialize_task(updated_task)


async def get_all_tasks(
    page: int,
    limit: int,
    status_filter=None,
    priority_filter=None,
    assigned_to=None,
    search=None
):

    if page < 1:

        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error_code": 400,
                "message": "Page must be greater than or equal to 1"
            }
        )

    if limit < 1 or limit > 100:

        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error_code": 400,
                "message": "Limit must be between 1 and 100"
            }
        )

    query = {}

    if status_filter:

        query["status"] = status_filter.value

    if priority_filter:

        query["priority"] = priority_filter.value

    if assigned_to:

        query["assigned_to"] = validate_object_id(
            assigned_to,
            "assigned user ID"
        )

    if search:

        query["title"] = {
            "$regex": search.strip(),
            "$options": "i"
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
        "data": tasks
    }