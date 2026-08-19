from fastapi import APIRouter, HTTPException, Query, status

from app.models.user import (
    UserRegister,
    UserLogin,
    APIResponse
)

from app.services.auth_service import (
    register_user,
    login_user,
    get_user_profile
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ============================================================
# Register User
# ============================================================

@router.post(
    "/register",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(user: UserRegister):

    result = await register_user(
        username=user.username,
        email=str(user.email),
        password=user.password
    )

    if not result["success"]:

        if result["error_code"] == "USER_ALREADY_EXISTS":

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=result
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error_code": "REGISTRATION_FAILED",
                "message": "User registration failed",
                "data": None
            }
        )

    return result


# ============================================================
# Login User
# ============================================================

@router.post(
    "/login",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK
)
async def login(user: UserLogin):

    result = await login_user(
        email=str(user.email),
        password=user.password
    )

    if not result["success"]:

        if result["error_code"] == "INVALID_CREDENTIALS":

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result
        )

    return result


# ============================================================
# Get User Profile
# ============================================================

@router.get(
    "/profile",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK
)
async def profile(
    email: str = Query(
        ...,
        description="Email address of the user"
    )
):

    result = await get_user_profile(email)

    if not result["success"]:

        if result["error_code"] == "USER_NOT_FOUND":

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result
        )

    return result