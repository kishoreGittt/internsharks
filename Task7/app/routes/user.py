from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from bson import ObjectId

from app.database.mongodb import users_collection
from app.auth.jwt_handler import decode_access_token


router = APIRouter(
    tags=["User"]
)


security = HTTPBearer(
    auto_error=False
)


# ============================================================
# Get Current User from JWT
# ============================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    # --------------------------------------------------------
    # 1. Check Authorization header
    # --------------------------------------------------------

    if credentials is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "AUTH_TOKEN_MISSING",
                "message": "Authorization token is required"
            }
        )

    # --------------------------------------------------------
    # 2. Get Bearer token
    # --------------------------------------------------------

    token = credentials.credentials

    # --------------------------------------------------------
    # 3. Decode JWT
    # --------------------------------------------------------

    try:

        payload = decode_access_token(token)

    except ValueError as error:

        if str(error) == "TOKEN_EXPIRED":

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "success": False,
                    "error_code": "AUTH_TOKEN_EXPIRED",
                    "message": "Access token has expired"
                }
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "AUTH_TOKEN_INVALID",
                "message": "Invalid or malformed access token"
            }
        )

    # --------------------------------------------------------
    # 4. Get user ID from JWT
    # --------------------------------------------------------

    user_id = payload.get("sub")

    if not user_id:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "AUTH_TOKEN_INVALID",
                "message": "Token does not contain user identity"
            }
        )

    # --------------------------------------------------------
    # 5. Validate MongoDB ObjectId
    # --------------------------------------------------------

    if not ObjectId.is_valid(user_id):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error_code": "AUTH_TOKEN_INVALID",
                "message": "Invalid user ID in token"
            }
        )

    # --------------------------------------------------------
    # 6. Find user in MongoDB
    # --------------------------------------------------------

    current_user = await users_collection.find_one(
        {
            "_id": ObjectId(user_id)
        }
    )

    if current_user is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error_code": "USER_NOT_FOUND",
                "message": "User associated with token was not found"
            }
        )

    return current_user


# ============================================================
# GET /me
# ============================================================

@router.get("/me")
async def get_me(
    current_user: dict = Depends(get_current_user)
):

    return {
        "success": True,
        "message": "Current user retrieved successfully",
        "data": {
            "id": str(current_user["_id"]),
            "username": current_user["username"],
            "email": current_user["email"]
        }
    }