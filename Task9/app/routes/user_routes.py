from fastapi import APIRouter, Depends

from app.dependencies.auth_dependency import (
    get_current_user
)


router = APIRouter(
    tags=["Users"]
)


@router.get("/me")
async def get_my_profile(
    current_user: dict = Depends(get_current_user)
):

    return {
        "success": True,
        "message": "User profile retrieved successfully",
        "data": {
            "id": current_user["_id"],
            "username": current_user["username"],
            "email": current_user["email"],
            "full_name": current_user.get("full_name"),
            "phone": current_user.get("phone"),
            "is_active": current_user.get("is_active", True)
        }
    }