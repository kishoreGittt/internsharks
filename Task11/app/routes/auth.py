from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from app.auth.jwt_handler import (
    create_access_token,
    hash_refresh_token,
)
from app.database.mongodb import (
    refresh_tokens_collection,
    users_collection,
)
from app.models.user import UserLogin, UserRegister
from app.services.auth_service import (
    login_user,
    register_user,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
async def register(data: UserRegister):

    user = await register_user(data)

    return {
        "success": True,
        "message": "User registered successfully",
        "data": user,
    }


@router.post("/login")
async def login(data: UserLogin):

    tokens = await login_user(data)

    return {
        "success": True,
        "message": "Login successful",
        "data": tokens,
    }


@router.post("/refresh")
async def refresh_token(
    refresh_token: str
):
    token_hash = hash_refresh_token(
        refresh_token
    )

    stored_token = await refresh_tokens_collection.find_one(
        {
            "token_hash": token_hash,
            "revoked": False,
        }
    )

    if stored_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if stored_token["expires_at"] <= datetime.now(
        timezone.utc
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )

    user = await users_collection.find_one(
        {"_id": stored_token["user_id"]}
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User authentication is invalid",
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )

    # Get current role from MongoDB
    role = user.get("role", "user")

    access_token = create_access_token(
        user_id=str(user["_id"]),
        role=role,
    )

    return {
        "success": True,
        "message": "Access token refreshed successfully",
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
        },
    }


@router.post("/logout")
async def logout(
    refresh_token: str
):

    token_hash = hash_refresh_token(
        refresh_token
    )

    result = await refresh_tokens_collection.update_one(
        {
            "token_hash": token_hash,
            "revoked": False,
        },
        {
            "$set": {
                "revoked": True
            }
        },
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    return {
        "success": True,
        "message": "Logout successful",
    }