from datetime import datetime, timezone
from typing import Optional

from app.storage.mongodb import projects_collection


def utc_now():
    return datetime.now(timezone.utc)


# =========================================================
# CREATE PROJECT
# =========================================================

async def create_project(project: dict):
    project["created_at"] = utc_now()
    project["updated_at"] = utc_now()

    await projects_collection.insert_one(project)

    return project


# =========================================================
# GET PROJECT
# =========================================================

async def get_project(
    user_id: str,
    project_id: Optional[str] = None,
    project_name: Optional[str] = None
) -> Optional[dict]:

    query = {
        "user_id": user_id
    }

    if project_id:
        query["project_id"] = project_id

    elif project_name:
        query["name"] = {
            "$regex": f"^{project_name}$",
            "$options": "i"
        }

    else:
        return None

    return await projects_collection.find_one(
        query,
        {"_id": 0}
    )


async def get_project_by_id(
    user_id: str,
    project_id: str
) -> Optional[dict]:

    return await get_project(
        user_id=user_id,
        project_id=project_id
    )


async def get_project_by_name(
    user_id: str,
    project_name: str
) -> Optional[dict]:

    return await get_project(
        user_id=user_id,
        project_name=project_name
    )


# =========================================================
# PROJECT MEMBERS
# =========================================================

async def get_project_members(
    user_id: str,
    project_id: str
):

    project = await get_project(
        user_id=user_id,
        project_id=project_id
    )

    if not project:
        return None

    return project.get("members", [])


# Compatibility name used by project_tools.py
async def get_members(
    user_id: str,
    project_id: str
):

    return await get_project_members(
        user_id=user_id,
        project_id=project_id
    )


# =========================================================
# PROJECT TASKS
# =========================================================

async def get_project_tasks(
    user_id: str,
    project_id: str
):

    project = await get_project(
        user_id=user_id,
        project_id=project_id
    )

    if not project:
        return None

    return project.get("tasks", [])


# Compatibility name
async def get_tasks(
    user_id: str,
    project_id: str
):

    return await get_project_tasks(
        user_id=user_id,
        project_id=project_id
    )


# =========================================================
# CREATE TASK
# =========================================================

async def create_project_task(
    user_id: str,
    project_id: str,
    title: str,
    description: str,
    assigned_to: Optional[str] = None
):

    project = await get_project(
        user_id=user_id,
        project_id=project_id
    )

    if not project:
        return None

    task = {
        "task_id": (
            f"task_"
            f"{int(datetime.now().timestamp() * 1000)}"
        ),
        "title": title,
        "description": description,
        "assigned_to": assigned_to,
        "status": "todo",
        "created_at": utc_now()
    }

    result = await projects_collection.update_one(
        {
            "user_id": user_id,
            "project_id": project_id
        },
        {
            "$push": {
                "tasks": task
            },
            "$set": {
                "updated_at": utc_now()
            }
        }
    )

    if result.matched_count == 0:
        return None

    return task


# Compatibility name used by project_tools.py
async def create_task(
    user_id: str,
    project_id: str,
    title: str,
    description: str,
    assigned_to: Optional[str] = None
):

    return await create_project_task(
        user_id=user_id,
        project_id=project_id,
        title=title,
        description=description,
        assigned_to=assigned_to
    )


# =========================================================
# UPDATE TASK STATUS
# =========================================================

async def update_project_task_status(
    user_id: str,
    project_id: str,
    task_id: str,
    status: str
):

    allowed_statuses = {
        "todo",
        "in_progress",
        "done",
        "blocked"
    }

    if status not in allowed_statuses:
        raise ValueError(
            "Invalid task status. Allowed values: "
            "todo, in_progress, done, blocked."
        )

    result = await projects_collection.update_one(
        {
            "user_id": user_id,
            "project_id": project_id,
            "tasks.task_id": task_id
        },
        {
            "$set": {
                "tasks.$.status": status,
                "updated_at": utc_now()
            }
        }
    )

    return result.modified_count > 0


# Compatibility name
async def update_task_status(
    user_id: str,
    project_id: str,
    task_id: str,
    status: str
):

    return await update_project_task_status(
        user_id=user_id,
        project_id=project_id,
        task_id=task_id,
        status=status
    )