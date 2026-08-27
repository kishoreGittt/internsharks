from fastapi import APIRouter, Depends

from app.auth.dependencies import require_admin
from app.models.task import TaskAssign
from app.services.task_service import (
    assign_task,
    get_tasks,
)
from app.services.user_service import get_all_users


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/users")
async def get_users(
    current_user=Depends(require_admin)
):

    users = await get_all_users()

    return {
        "success": True,
        "message": "Users retrieved successfully",
        "data": users,
    }


@router.get("/tasks")
async def get_admin_tasks(
    page: int = 1,
    limit: int = 10,
    status: str | None = None,
    priority: str | None = None,
    assigned_to: str | None = None,
    search: str | None = None,
    current_user=Depends(require_admin),
):

    return await get_tasks(
        current_user=current_user,
        page=page,
        limit=limit,
        task_status=status,
        priority=priority,
        assigned_to=assigned_to,
        search=search,
    )


@router.patch("/tasks/{task_id}/assign")
async def assign(
    task_id: str,
    data: TaskAssign,
    current_user=Depends(require_admin)
):

    task = await assign_task(
        task_id,
        data.user_id
    )

    return {
        "success": True,
        "message": "Task assigned successfully",
        "data": task,
    }