from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt import decode_access_token


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        payload = decode_access_token(token)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "status_code": 401,
                "error": "INVALID_TOKEN",
                "message": "Invalid or expired token.",
            },
        )

    user_id = payload.get("user_id")
    email = payload.get("email")

    if not user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "status_code": 401,
                "error": "INVALID_TOKEN",
                "message": "Token does not contain required user information.",
            },
        )

    return {
        "user_id": user_id,
        "email": email,
        "name": payload.get("name"),
        "role": payload.get("role", "user"),
    }