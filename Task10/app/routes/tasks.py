from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import get_current_user

from app.models.task import (
    TaskCreate,
    TaskUpdate,
    TaskStatusUpdate,
    TaskStatus,
    TaskPriority
)

from app.services.task_service import (
    create_task,
    get_user_tasks,
    get_task_by_id,
    update_task,
    update_task_status,
    delete_task
)


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@router.post("", status_code=201)
async def create_new_task(
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
        "data": task
    }


@router.get("")
async def get_tasks(
    page: int = Query(default=1),
    limit: int = Query(default=10),
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    assigned_to: str | None = None,
    search: str | None = None,
    current_user=Depends(get_current_user)
):

    return await get_user_tasks(
        current_user=current_user,
        page=page,
        limit=limit,
        status_filter=status,
        priority_filter=priority,
        assigned_to=assigned_to,
        search=search
    )


@router.get("/{task_id}")
async def get_single_task(
    task_id: str,
    current_user=Depends(get_current_user)
):

    task = await get_task_by_id(
        task_id,
        current_user
    )

    return {
        "success": True,
        "message": "Task retrieved successfully",
        "data": task
    }


@router.put("/{task_id}")
async def update_existing_task(
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
        "data": task
    }


@router.patch("/{task_id}/status")
async def change_task_status(
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
        "data": task
    }


@router.delete("/{task_id}")
async def remove_task(
    task_id: str,
    current_user=Depends(get_current_user)
):

    await delete_task(
        task_id,
        current_user
    )

    return {
        "success": True,
        "message": "Task deleted successfully",
        "data": None
    }