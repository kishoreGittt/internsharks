from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me")
async def get_my_profile(
    current_user=Depends(get_current_user)
):

    return {
        "success": True,
        "message": "Profile retrieved successfully",
        "data": {
            "id": current_user["id"],
            "username": current_user["username"],
            "email": current_user["email"],
            "role": current_user["role"],
            "is_active": current_user["is_active"]
        }
    }