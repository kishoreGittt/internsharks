import logging

from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from jose import JWTError

from app.auth.jwt_handler import decode_access_token
from app.database.mongodb import users_collection


logger = logging.getLogger(__name__)


security = HTTPBearer(
    auto_error=False
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    )
):
    # No Authorization header
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    token = credentials.credentials

    try:
        payload = decode_access_token(token)

    except JWTError:
        logger.warning(
            "Authorization failure: invalid access token"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )

    user_id = payload.get("sub")

    if not user_id or not ObjectId.is_valid(user_id):
        logger.warning(
            "Authorization failure: invalid user ID"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    user = await users_collection.find_one(
        {"_id": ObjectId(user_id)}
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )

    # Always use the CURRENT role from MongoDB.
    # This means role changes are reflected after a new request.
    role = user.get("role", "user")

    current_user = {
        "id": str(user["_id"]),
        "username": user.get("username"),
        "email": user.get("email"),
        "full_name": user.get("full_name"),
        "phone": user.get("phone"),
        "department": user.get("department"),
        "role": role,
        "is_active": user.get("is_active", True),
    }

    return current_user


def require_admin(
    current_user=Depends(get_current_user)
):
    if current_user.get("role") != "admin":

        logger.warning(
            "Authorization failure: "
            "non-admin attempted admin operation "
            "user_id=%s",
            current_user.get("id")
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )

    return current_user