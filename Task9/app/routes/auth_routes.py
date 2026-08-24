from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from uuid import uuid4

from app.database.mongodb import (
    users_collection,
    refresh_sessions_collection
)

from app.schemas.auth_schema import (
    RegisterRequest,
    LoginRequest
)

from app.services.auth_service import (
    hash_password,
    verify_password
)

from app.services.token_service import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_jti
)

from app.models.refresh_session import (
    create_refresh_session_document
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

security = HTTPBearer()


# ============================================================
# REGISTER
# ============================================================

@router.post("/register")
async def register_user(
    request: RegisterRequest
):

    existing_user = await users_collection.find_one(
        {"email": request.email}
    )

    if existing_user:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "success": False,
                "error_code": "EMAIL_ALREADY_EXISTS",
                "message": "Email already registered"
            }
        )

    existing_username = await users_collection.find_one(
        {"username": request.username}
    )

    if existing_username:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "success": False,
                "error_code": "USERNAME_ALREADY_EXISTS",
                "message": "Username already exists"
            }
        )

    user_id = str(uuid4())

    hashed_password = hash_password(
        request.password
    )

    user_document = {
        "_id": user_id,
        "username": request.username,
        "email": request.email,
        "password": hashed_password,
        "full_name": request.full_name,
        "phone": request.phone,
        "is_active": True
    }

    await users_collection.insert_one(
        user_document
    )

    return {
        "success": True,
        "message": "User registered successfully",
        "data": {
            "id": user_id,
            "username": request.username,
            "email": request.email,
            "full_name": request.full_name,
            "phone": request.phone,
            "is_active": True
        }
    }


# ============================================================
# LOGIN
# ============================================================

@router.post("/login")
async def login_user(
    request: LoginRequest
):

    user = await users_collection.find_one(
        {"email": request.email}
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password"
            }
        )

    password_valid = verify_password(
        request.password,
        user["password"]
    )

    if not password_valid:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password"
            }
        )

    if not user.get("is_active", True):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "error_code": "USER_INACTIVE",
                "message": "User account is inactive"
            }
        )

    access_token = create_access_token(
        user["_id"]
    )

    refresh_token, jti, expires_at = create_refresh_token(
        user["_id"]
    )

    jti_hash = hash_jti(jti)

    session_document = create_refresh_session_document(
        user_id=user["_id"],
        jti_hash=jti_hash,
        expires_at=expires_at
    )

    await refresh_sessions_collection.insert_one(
        session_document
    )

    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    }


# ============================================================
# REFRESH TOKEN
# ============================================================

@router.post("/refresh")
async def refresh_access_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    payload = decode_token(token)

    if payload is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "INVALID_REFRESH_TOKEN",
                "message": "Invalid or expired refresh token"
            }
        )

    token_type = payload.get("type")

    if token_type != "refresh":

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "INVALID_TOKEN_TYPE",
                "message": "Access token cannot be used as a refresh token"
            }
        )

    user_id = payload.get("sub")
    jti = payload.get("jti")

    if not user_id or not jti:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "INVALID_REFRESH_TOKEN",
                "message": "Refresh token is missing required information"
            }
        )

    jti_hash = hash_jti(jti)

    session = await refresh_sessions_collection.find_one(
        {
            "jti_hash": jti_hash,
            "user_id": user_id
        }
    )

    if not session:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "SESSION_NOT_FOUND",
                "message": "Refresh session is invalid or has been revoked"
            }
        )

    if session.get("revoked", False):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "REFRESH_TOKEN_REVOKED",
                "message": "Refresh token has been revoked"
            }
        )

    expires_at = session.get("expires_at")

    if expires_at:

        if expires_at.tzinfo is None:

            expires_at = expires_at.replace(
                tzinfo=timezone.utc
            )

        if expires_at <= datetime.now(timezone.utc):

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "success": False,
                    "error_code": "REFRESH_TOKEN_EXPIRED",
                    "message": "Refresh token has expired"
                }
            )

    user = await users_collection.find_one(
        {"_id": user_id}
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "USER_NOT_FOUND",
                "message": "User no longer exists"
            }
        )

    if not user.get("is_active", True):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "error_code": "USER_INACTIVE",
                "message": "User account is inactive"
            }
        )

    new_access_token = create_access_token(
        user_id
    )

    return {
        "success": True,
        "message": "Access token refreshed successfully",
        "data": {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    }


# ============================================================
# LOGOUT
# ============================================================

@router.post("/logout")
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    payload = decode_token(token)

    if payload is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "INVALID_TOKEN",
                "message": "Invalid or expired refresh token"
            }
        )

    if payload.get("type") != "refresh":

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "INVALID_TOKEN_TYPE",
                "message": "Logout requires a refresh token"
            }
        )

    jti = payload.get("jti")

    if not jti:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "INVALID_REFRESH_TOKEN",
                "message": "Refresh token is missing session information"
            }
        )

    jti_hash = hash_jti(jti)

    session = await refresh_sessions_collection.find_one(
        {"jti_hash": jti_hash}
    )

    if not session:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "SESSION_NOT_FOUND",
                "message": "Refresh session not found"
            }
        )

    if session.get("revoked", False):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "SESSION_ALREADY_REVOKED",
                "message": "Refresh session is already logged out"
            }
        )

    await refresh_sessions_collection.update_one(
        {"jti_hash": jti_hash},
        {
            "$set": {
                "revoked": True,
                "revoked_at": datetime.now(timezone.utc)
            }
        }
    )

    return {
        "success": True,
        "message": "Logout successful",
        "data": None
    }