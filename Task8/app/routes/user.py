from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from app.auth.dependencies import get_current_user

from app.models.user import (
    UserResponse,
    ProfileUpdateRequest
)

from app.services.user_service import (
    serialize_user,
    update_own_profile
)


router = APIRouter(
    tags=["User"]
)


@router.get(
    "/me",
    response_model=UserResponse
)
async def get_my_profile(
    current_user=Depends(get_current_user)
):

    return serialize_user(current_user)


@router.put(
    "/me",
    response_model=UserResponse
)
async def update_my_profile(
    data: ProfileUpdateRequest,
    current_user=Depends(get_current_user)
):

    updated_user, success, error = (
        await update_own_profile(
            current_user,
            data
        )
    )


    if error == "NO_UPDATE_FIELDS":

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": "No profile fields provided for update",
                "error_code": "NO_UPDATE_FIELDS"
            }
        )


    if error == "USERNAME_EXISTS":

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "success": False,
                "message": "Username already exists",
                "error_code": "USERNAME_ALREADY_EXISTS"
            }
        )


    return serialize_user(updated_user)