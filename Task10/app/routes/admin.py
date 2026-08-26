from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import get_current_admin

from app.models.task import (
    TaskAssign,
    TaskStatus,
    TaskPriority
)

from app.services.user_service import get_all_users

from app.services.task_service import (
    get_all_tasks,
    assign_task
)


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# @router.get("/users")
# async def get_users(
#     current_admin=Depends(get_current_admin)
# ):

#     users = await get_all_users()

#     return {
#         "success": True,
#         "message": "Users retrieved successfully",
#         "data": users
#     }



@router.get("/users")
async def get_users(
    current_admin=Depends(get_current_admin)
):
    users = await get_all_users()

    return {
        "success": True,
        "message": "Users retrieved successfully",
        "data": users
    }





@router.get("/tasks")
async def get_admin_tasks(
    page: int = Query(default=1),
    limit: int = Query(default=10),
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    assigned_to: str | None = None,
    search: str | None = None,
    current_admin=Depends(get_current_admin)
):

    return await get_all_tasks(
        page=page,
        limit=limit,
        status_filter=status,
        priority_filter=priority,
        assigned_to=assigned_to,
        search=search
    )


@router.patch("/tasks/{task_id}/assign")
async def assign_task_to_user(
    task_id: str,
    data: TaskAssign,
    current_admin=Depends(get_current_admin)
):

    task = await assign_task(
        task_id,
        data.user_id
    )

    return {
        "success": True,
        "message": "Task assigned successfully",
        "data": task
    }