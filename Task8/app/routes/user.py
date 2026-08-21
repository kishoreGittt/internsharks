from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from app.auth.dependencies import (
    get_current_user
)

from app.models.user import (
    UserUpdate
)

from app.services.user_service import (
    serialize_user,
    update_own_profile
)


router = APIRouter(
    tags=["User"]
)


# ============================================================
# GET /me
# ============================================================

@router.get("/me")
async def get_my_profile(
    current_user=Depends(
        get_current_user
    )
):

    return {
        "success": True,
        "message": "Profile retrieved successfully",
        "data": serialize_user(
            current_user
        )
    }


# ============================================================
# PUT /me
# ============================================================

@router.put("/me")
async def update_my_profile(

    data: UserUpdate,

    current_user=Depends(
        get_current_user
    )
):

    updated_user, error = await update_own_profile(

        current_user,

        data
    )


    # --------------------------------------------------------
    # Duplicate username
    # --------------------------------------------------------

    if error == "USERNAME_EXISTS":

        raise HTTPException(
            status_code=409,
            detail={
                "success": False,
                "message": "Username already exists",
                "error_code": "USERNAME_ALREADY_EXISTS"
            }
        )


    # --------------------------------------------------------
    # Success
    # --------------------------------------------------------

    return {

        "success": True,

        "message": "Profile updated successfully",

        "data": serialize_user(
            updated_user
        )
    }