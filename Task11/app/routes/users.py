from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.models.user import UserUpdate
from app.services.user_service import update_current_user


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me")
async def get_me(
    current_user=Depends(get_current_user)
):

    return {
        "success": True,
        "message": "Profile retrieved successfully",
        "data": current_user,
    }


@router.put("/me")
async def update_me(
    data: UserUpdate,
    current_user=Depends(get_current_user)
):

    user = await update_current_user(
        current_user["id"],
        data
    )

    return {
        "success": True,
        "message": "Profile updated successfully",
        "data": user,
    }