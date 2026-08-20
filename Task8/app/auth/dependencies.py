from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth.jwt_handler import decode_access_token
from app.database.mongodb import users_collection


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    payload = decode_access_token(token)

    if payload is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "message": "Invalid or expired JWT token",
                "error_code": "INVALID_TOKEN"
            }
        )

    email = payload.get("sub")

    if not email:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "message": "Invalid token payload",
                "error_code": "INVALID_TOKEN_PAYLOAD"
            }
        )

    user = await users_collection.find_one(
        {"email": email}
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "message": "User no longer exists",
                "error_code": "USER_NOT_FOUND"
            }
        )

    if not user.get("is_active", True):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "message": "Your account is deactivated",
                "error_code": "ACCOUNT_INACTIVE"
            }
        )

    return user


async def require_admin(
    current_user=Depends(get_current_user)
):

    if current_user.get("role") != "admin":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "message": "Admin access required",
                "error_code": "INSUFFICIENT_PERMISSION"
            }
        )

    return current_user