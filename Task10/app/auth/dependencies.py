from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

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
                "error_code": 401,
                "message": "Invalid or expired access token"
            }
        )

    user_id = payload.get("sub")

    from bson import ObjectId

    if not ObjectId.is_valid(user_id):

        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error_code": 401,
                "message": "Invalid user identity"
            }
        )

    user = await users_collection.find_one(
        {
            "_id": ObjectId(user_id)
        }
    )

    if user is None:

        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error_code": 404,
                "message": "User not found"
            }
        )

    if not user.get("is_active", True):

        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "error_code": 403,
                "message": "User account is inactive"
            }
        )

    user["id"] = str(user["_id"])

    return user


async def get_current_admin(
    current_user=Depends(get_current_user)
):

    if current_user.get("role") != "admin":

        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "error_code": 403,
                "message": "Admin access required"
            }
        )

    return current_user