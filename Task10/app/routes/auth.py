# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel, Field

# from app.models.user import UserRegister, UserLogin
# from app.services.auth_service import (
#     register_user,
#     login_user,
#     refresh_access_token,
#     logout_user
# )


# router = APIRouter(
#     prefix="/auth",
#     tags=["Authentication"]
# )


# class RefreshTokenRequest(BaseModel):

#     refresh_token: str = Field(
#         ...,
#         min_length=1
#     )


# @router.post(
#     "/register",
#     status_code=201
# )
# async def register(data: UserRegister):

#     user = await register_user(data)

#     return {
#         "success": True,
#         "message": "User registered successfully",
#         "data": user
#     }


# @router.post("/login")
# async def login(data: UserLogin):

#     tokens = await login_user(data)

#     return {
#         "success": True,
#         "message": "Login successful",
#         "data": tokens
#     }


# @router.post("/refresh")
# async def refresh(data: RefreshTokenRequest):

#     tokens = await refresh_access_token(
#         data.refresh_token
#     )

#     return {
#         "success": True,
#         "message": "Access token refreshed successfully",
#         "data": tokens
#     }


# @router.post("/logout")
# async def logout(data: RefreshTokenRequest):

#     await logout_user(
#         data.refresh_token
#     )

#     return {
#         "success": True,
#         "message": "Logout successful",
#         "data": None
#     }



from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.models.user import UserRegister, UserLogin

from app.services.auth_service import (
    register_user,
    login_user,
    refresh_access_token,
    logout_user
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


class RefreshTokenRequest(BaseModel):

    refresh_token: str = Field(
        ...,
        min_length=1
    )


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    status_code=201
)
async def register(data: UserRegister):

    user = await register_user(data)

    return {
        "success": True,
        "message": "User registered successfully",
        "data": user
    }


# ============================================================
# LOGIN
# ============================================================

@router.post("/login")
async def login(data: UserLogin):

    tokens = await login_user(data)

    return {
        "success": True,
        "message": "Login successful",
        "data": tokens
    }


# ============================================================
# REFRESH TOKEN
# ============================================================

@router.post("/refresh")
async def refresh(data: RefreshTokenRequest):

    tokens = await refresh_access_token(
        data.refresh_token
    )

    return {
        "success": True,
        "message": "Access token refreshed successfully",
        "data": tokens
    }


# ============================================================
# LOGOUT
# ============================================================

@router.post("/logout")
async def logout(data: RefreshTokenRequest):

    await logout_user(
        data.refresh_token
    )

    return {
        "success": True,
        "message": "Logout successful",
        "data": None
    }