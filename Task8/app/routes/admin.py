from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)

from app.auth.dependencies import require_admin

from app.models.user import (
    UserResponse,
    RoleUpdateRequest,
    StatusUpdateRequest
)

from app.services.user_service import (
    get_all_users,
    get_user_by_id,
    serialize_user,
    update_user_role,
    update_user_status,
    delete_user
)


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/users")
async def get_users(
    role: Optional[str] = Query(
        default=None,
        pattern="^(user|admin)$"
    ),

    department: Optional[str] = None,

    is_active: Optional[bool] = None,

    current_admin=Depends(require_admin)
):

    users = await get_all_users(
        role=role,
        department=department,
        is_active=is_active
    )

    return {
        "success": True,
        "message": "Users retrieved successfully",
        "data": users
    }


@router.get(
    "/users/{user_id}",
    response_model=UserResponse
)
async def get_single_user(
    user_id: str,
    current_admin=Depends(require_admin)
):

    user = await get_user_by_id(user_id)

    if not user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "message": "User not found",
                "error_code": "USER_NOT_FOUND"
            }
        )

    return serialize_user(user)


@router.patch(
    "/users/{user_id}/role",
    response_model=UserResponse
)
async def change_user_role(
    user_id: str,
    data: RoleUpdateRequest,
    current_admin=Depends(require_admin)
):

    # Prevent admin from accidentally removing
    # their own admin access.
    if str(current_admin["_id"]) == user_id:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": "You cannot change your own role",
                "error_code": "SELF_ROLE_CHANGE_NOT_ALLOWED"
            }
        )


    updated_user = await update_user_role(
        user_id,
        data.role
    )

    if not updated_user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "message": "User not found",
                "error_code": "USER_NOT_FOUND"
            }
        )


    return serialize_user(updated_user)


@router.patch(
    "/users/{user_id}/status",
    response_model=UserResponse
)
async def change_user_status(
    user_id: str,
    data: StatusUpdateRequest,
    current_admin=Depends(require_admin)
):

    # Prevent admin from deactivating themselves.
    if str(current_admin["_id"]) == user_id:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": "You cannot change your own account status",
                "error_code": "SELF_STATUS_CHANGE_NOT_ALLOWED"
            }
        )


    updated_user = await update_user_status(
        user_id,
        data.is_active
    )

    if not updated_user:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "message": "User not found",
                "error_code": "USER_NOT_FOUND"
            }
        )


    return serialize_user(updated_user)


@router.delete(
    "/users/{user_id}"
)
async def remove_user(
    user_id: str,
    current_admin=Depends(require_admin)
):

    if str(current_admin["_id"]) == user_id:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": "You cannot delete your own account",
                "error_code": "SELF_DELETE_NOT_ALLOWED"
            }
        )


    deleted = await delete_user(user_id)

    if not deleted:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "message": "User not found",
                "error_code": "USER_NOT_FOUND"
            }
        )


    return {
        "success": True,
        "message": "User deleted successfully",
        "data": None
    }