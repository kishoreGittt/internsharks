import uuid

from pydantic import BaseModel, Field, model_validator

from app.storage.repositories.project_repository import (
    get_project,
    get_members,
    get_tasks,
    create_task,
    update_task_status
)


class GetProjectArgs(BaseModel):

    project_id: str | None = None

    project_name: str | None = None

    @model_validator(mode="after")
    def validate_input(self):

        if not self.project_id and not self.project_name:

            raise ValueError(
                "project_id or project_name is required."
            )

        return self


class ProjectIdArgs(BaseModel):

    project_id: str


class CreateTaskArgs(BaseModel):

    project_id: str

    title: str = Field(
        min_length=1,
        max_length=200
    )

    description: str = Field(
        default="",
        max_length=1000
    )


class UpdateTaskStatusArgs(BaseModel):

    project_id: str

    task_id: str

    status: str

    @model_validator(mode="after")
    def validate_status(self):

        allowed = {
            "pending",
            "in_progress",
            "completed",
            "cancelled"
        }

        if self.status not in allowed:

            raise ValueError(
                f"Invalid status. Allowed: {sorted(allowed)}"
            )

        return self


async def tool_get_project(
    owner_id: str,
    arguments: dict
):

    args = GetProjectArgs.model_validate(
        arguments
    )

    project = await get_project(
        owner_id=owner_id,
        project_id=args.project_id,
        project_name=args.project_name
    )

    if not project:

        return {
            "success": False,
            "error": "PROJECT_NOT_FOUND"
        }

    return project


async def tool_get_project_members(
    owner_id: str,
    arguments: dict
):

    args = ProjectIdArgs.model_validate(
        arguments
    )

    members = await get_members(
        owner_id,
        args.project_id
    )

    if members is None:

        return {
            "success": False,
            "error": "PROJECT_NOT_FOUND"
        }

    return {
        "success": True,
        "members": members
    }


async def tool_get_project_tasks(
    owner_id: str,
    arguments: dict
):

    args = ProjectIdArgs.model_validate(
        arguments
    )

    tasks = await get_tasks(
        owner_id,
        args.project_id
    )

    if tasks is None:

        return {
            "success": False,
            "error": "PROJECT_NOT_FOUND"
        }

    return {
        "success": True,
        "tasks": tasks
    }


async def tool_create_project_task(
    owner_id: str,
    arguments: dict
):

    args = CreateTaskArgs.model_validate(
        arguments
    )

    task = {
        "task_id": str(
            uuid.uuid4()
        ),
        "title": args.title,
        "description": args.description,
        "status": "pending"
    }

    created = await create_task(
        owner_id,
        args.project_id,
        task
    )

    if not created:

        return {
            "success": False,
            "error": "PROJECT_NOT_FOUND"
        }

    return {
        "success": True,
        "task": task
    }


async def tool_update_project_task_status(
    owner_id: str,
    arguments: dict
):

    args = UpdateTaskStatusArgs.model_validate(
        arguments
    )

    updated = await update_task_status(
        owner_id,
        args.project_id,
        args.task_id,
        args.status
    )

    if not updated:

        return {
            "success": False,
            "error": "TASK_NOT_FOUND"
        }

    return {
        "success": True,
        "task_id": args.task_id,
        "status": args.status
    }