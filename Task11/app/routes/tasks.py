from fastapi import APIRouter, Depends, Query, status

from app.auth.dependencies import get_current_user
from app.models.task import (
    TaskCreate,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.services.task_service import (
    create_task,
    delete_task,
    get_task,
    get_tasks,
    update_task,
    update_task_status,
)


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED
)
async def create(
    data: TaskCreate,
    current_user=Depends(get_current_user)
):

    task = await create_task(
        data,
        current_user
    )

    return {
        "success": True,
        "message": "Task created successfully",
        "data": task,
    }


@router.get("")
async def list_tasks(
    page: int = Query(default=1),
    limit: int = Query(default=10),
    task_status: str | None = Query(
        default=None,
        alias="status"
    ),
    priority: str | None = None,
    assigned_to: str | None = None,
    search: str | None = None,
    current_user=Depends(get_current_user),
):

    return await get_tasks(
        current_user=current_user,
        page=page,
        limit=limit,
        task_status=task_status,
        priority=priority,
        assigned_to=assigned_to,
        search=search,
    )


@router.get("/{task_id}")
async def get_single_task(
    task_id: str,
    current_user=Depends(get_current_user)
):

    task = await get_task(
        task_id,
        current_user
    )

    return {
        "success": True,
        "message": "Task retrieved successfully",
        "data": task,
    }


@router.put("/{task_id}")
async def update(
    task_id: str,
    data: TaskUpdate,
    current_user=Depends(get_current_user)
):

    task = await update_task(
        task_id,
        data,
        current_user
    )

    return {
        "success": True,
        "message": "Task updated successfully",
        "data": task,
    }


@router.patch("/{task_id}/status")
async def update_status(
    task_id: str,
    data: TaskStatusUpdate,
    current_user=Depends(get_current_user)
):

    task = await update_task_status(
        task_id,
        data,
        current_user
    )

    return {
        "success": True,
        "message": "Task status updated successfully",
        "data": task,
    }


@router.delete("/{task_id}")
async def delete(
    task_id: str,
    current_user=Depends(get_current_user)
):

    return await delete_task(
        task_id,
        current_user
    )