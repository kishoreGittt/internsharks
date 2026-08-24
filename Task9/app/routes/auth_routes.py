from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest
)

from app.services.auth_service import (
    register_user,
    authenticate_user,
    create_login_tokens,
    get_user_by_id,
    get_refresh_session,
    revoke_refresh_session
)

from app.services.token_service import (
    decode_token,
    hash_jti,
    create_access_token
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

security = HTTPBearer()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):

    user = await register_user(
        username=request.username,
        email=request.email,
        password=request.password,
        full_name=request.full_name,
        phone=request.phone
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "success": False,
                "error_code": "EMAIL_ALREADY_EXISTS",
                "message": "Email already registered"
            }
        )

    return {
        "success": True,
        "message": "User registered successfully",
        "data": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"]
        }
    }


@router.post("/login")
async def login(request: LoginRequest):

    user, error = await authenticate_user(
        email=request.email,
        password=request.password
    )

    if error == "USER_NOT_FOUND":

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password"
            }
        )

    if error == "INVALID_PASSWORD":

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password"
            }
        )

    if error == "USER_INACTIVE":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "error_code": "USER_INACTIVE",
                "message": "User account is inactive"
            }
        )

    access_token, refresh_token = await create_login_tokens(
        user
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


@router.post("/refresh")
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    # Decode and validate JWT.
    try:
        payload = decode_token(token)

    except ValueError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "INVALID_REFRESH_TOKEN",
                "message": "Invalid or expired refresh token"
            }
        )

    # IMPORTANT:
    # Access tokens cannot be used here.
    if payload.get("type") != "refresh":

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "INVALID_TOKEN_TYPE",
                "message": "Refresh token required"
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

    # Check user.
    user = await get_user_by_id(user_id)

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "USER_NOT_FOUND",
                "message": "User no longer exists"
            }
        )

    # Check active status.
    if not user.get("is_active", True):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "error_code": "USER_INACTIVE",
                "message": "User account is inactive"
            }
        )

    # Find refresh session.
    jti_hash = hash_jti(jti)

    session = await get_refresh_session(
        user_id=user_id,
        jti_hash=jti_hash
    )

    if not session:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "SESSION_NOT_FOUND",
                "message": "Refresh session is invalid or revoked"
            }
        )

    # Check revoked.
    if session.get("revoked", False):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "SESSION_REVOKED",
                "message": "Refresh session has been revoked"
            }
        )

    # Create new access token.
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


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    try:
        payload = decode_token(token)

    except ValueError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "INVALID_REFRESH_TOKEN",
                "message": "Invalid or expired refresh token"
            }
        )

    # Logout requires a refresh token.
    if payload.get("type") != "refresh":

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "INVALID_TOKEN_TYPE",
                "message": "Refresh token required for logout"
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
                "message": "Invalid refresh token"
            }
        )

    jti_hash = hash_jti(jti)

    revoked = await revoke_refresh_session(
        user_id=user_id,
        jti_hash=jti_hash
    )

    if not revoked:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "SESSION_NOT_FOUND",
                "message": "Refresh session is already revoked or does not exist"
            }
        )

    return {
        "success": True,
        "message": "Logout successful",
        "data": None
    }