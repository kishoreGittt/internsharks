from typing import Optional

from app.services.project_service import (
    create_project_task,
    list_project_tasks,
    update_task_status
)


def create_project_task_tool(
    project_id: int,
    title: str,
    priority: str,
    assigned_to: Optional[int] = None
) -> dict:

    return create_project_task(
        project_id=project_id,
        title=title,
        priority=priority,
        assigned_to=assigned_to
    )


def list_project_tasks_tool(
    project_id: int
) -> dict:

    return list_project_tasks(
        project_id=project_id
    )


def update_task_status_tool(
    task_id: int,
    status: str
) -> dict:

    return update_task_status(
        task_id=task_id,
        status=status
    )