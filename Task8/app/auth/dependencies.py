from fastapi import (
    Depends,
    HTTPException,
    status
)

from fastapi.security import (
    OAuth2PasswordBearer
)

from jose import (
    JWTError,
    ExpiredSignatureError
)

from app.auth.jwt_handler import (
    decode_access_token
)

from app.database.mongodb import (
    users_collection
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# ============================================================
# GET CURRENT USER
# ============================================================

async def get_current_user(
    token: str = Depends(
        oauth2_scheme
    )
):

    try:

        payload = decode_access_token(
            token
        )

    except ExpiredSignatureError:

        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "message": "Token has expired",
                "error_code": "TOKEN_EXPIRED"
            }
        )

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "message": "Invalid JWT token",
                "error_code": "INVALID_TOKEN"
            }
        )

    email = payload.get(
        "sub"
    )

    if not email:

        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "message": "Invalid token payload",
                "error_code": "INVALID_TOKEN"
            }
        )

    user = await users_collection.find_one(
        {
            "email": email
        }
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "message": "User not found",
                "error_code": "USER_NOT_FOUND"
            }
        )

    # Check latest status from MongoDB
    if not user.get(
        "is_active",
        True
    ):

        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "message": "Account is deactivated",
                "error_code": "ACCOUNT_INACTIVE"
            }
        )

    return user


# ============================================================
# ADMIN CHECK
# ============================================================

async def require_admin(
    current_user=Depends(
        get_current_user
    )
):

    # Role comes from MongoDB,
    # NOT from client request.
    if current_user.get(
        "role"
    ) != "admin":

        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "message": "Admin access required",
                "error_code": "INSUFFICIENT_PERMISSION"
            }
        )

    return current_user