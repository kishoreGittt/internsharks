from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)

from app.auth.dependencies import (
    require_admin
)

from app.models.user import (
    RoleUpdate,
    StatusUpdate
)

from app.services.user_service import (
    get_all_users,
    get_user_by_id,
    serialize_user,
    change_user_role,
    change_user_status,
    delete_user
)


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# ============================================================
# GET ALL USERS
# ============================================================

@router.get(
    "/users"
)
async def get_users(

    role: Optional[str] = Query(
        default=None
    ),

    department: Optional[str] = Query(
        default=None
    ),

    is_active: Optional[bool] = Query(
        default=None
    ),

    admin=Depends(
        require_admin
    )
):

    # Validate role filter
    if role is not None:

        if role not in [
            "user",
            "admin"
        ]:

            raise HTTPException(
                status_code=422,
                detail={
                    "success": False,
                    "message": "Invalid role. Use user or admin",
                    "error_code": "INVALID_ROLE"
                }
            )


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


# ============================================================
# GET USER BY ID
# ============================================================

@router.get(
    "/users/{user_id}"
)
async def get_specific_user(

    user_id: str,

    admin=Depends(
        require_admin
    )
):

    user, error = await get_user_by_id(
        user_id
    )


    if error == "INVALID_ID":

        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "message": "Invalid user ID",
                "error_code": "INVALID_USER_ID"
            }
        )


    if error == "USER_NOT_FOUND":

        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "message": "User not found",
                "error_code": "USER_NOT_FOUND"
            }
        )


    return {

        "success": True,

        "message": "User retrieved successfully",

        "data": serialize_user(
            user
        )
    }


# ============================================================
# CHANGE ROLE
# ============================================================

@router.patch(
    "/users/{user_id}/role"
)
async def update_role(

    user_id: str,

    data: RoleUpdate,

    admin=Depends(
        require_admin
    )
):

    user, error = await change_user_role(

        user_id,

        data.role
    )


    if error == "INVALID_ID":

        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "message": "Invalid user ID",
                "error_code": "INVALID_USER_ID"
            }
        )


    if error == "USER_NOT_FOUND":

        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "message": "User not found",
                "error_code": "USER_NOT_FOUND"
            }
        )


    return {

        "success": True,

        "message": "User role updated successfully",

        "data": serialize_user(
            user
        )
    }


# ============================================================
# CHANGE STATUS
# ============================================================

@router.patch(
    "/users/{user_id}/status"
)
async def update_status(

    user_id: str,

    data: StatusUpdate,

    admin=Depends(
        require_admin
    )
):

    user, error = await change_user_status(

        user_id,

        data.is_active
    )


    if error == "INVALID_ID":

        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "message": "Invalid user ID",
                "error_code": "INVALID_USER_ID"
            }
        )


    if error == "USER_NOT_FOUND":

        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "message": "User not found",
                "error_code": "USER_NOT_FOUND"
            }
        )


    return {

        "success": True,

        "message": "User status updated successfully",

        "data": serialize_user(
            user
        )
    }


# ============================================================
# DELETE USER
# ============================================================

@router.delete(
    "/users/{user_id}"
)
async def remove_user(

    user_id: str,

    admin=Depends(
        require_admin
    )
):

    user, error = await delete_user(
        user_id
    )


    if error == "INVALID_ID":

        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "message": "Invalid user ID",
                "error_code": "INVALID_USER_ID"
            }
        )


    if error == "USER_NOT_FOUND":

        raise HTTPException(
            status_code=404,
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