# from datetime import datetime, timezone

# from fastapi import HTTPException
# from passlib.context import CryptContext

# from app.auth.jwt_handler import (
#     create_access_token,
#     create_refresh_expiry,
#     create_refresh_token,
#     hash_refresh_token
# )

# from app.database.mongodb import (
#     users_collection,
#     refresh_tokens_collection
# )


# pwd_context = CryptContext(
#     schemes=["bcrypt"],
#     deprecated="auto"
# )


# def hash_password(password: str):

#     return pwd_context.hash(password)


# def verify_password(
#     plain_password: str,
#     hashed_password: str
# ):

#     return pwd_context.verify(
#         plain_password,
#         hashed_password
#     )


# async def register_user(data):

#     existing_user = await users_collection.find_one(
#         {
#             "email": data.email.lower()
#         }
#     )

#     if existing_user:

#         raise HTTPException(
#             status_code=409,
#             detail={
#                 "success": False,
#                 "error_code": 409,
#                 "message": "Email already registered"
#             }
#         )

#     user_document = {
#         "username": data.username.strip(),
#         "email": data.email.lower(),
#         "password_hash": hash_password(data.password),
#         "role": "user",
#         "is_active": True,
#         "created_at": datetime.now(timezone.utc)
#     }

#     result = await users_collection.insert_one(
#         user_document
#     )

#     return {
#         "id": str(result.inserted_id),
#         "username": user_document["username"],
#         "email": user_document["email"],
#         "role": user_document["role"],
#         "is_active": user_document["is_active"]
#     }


# async def login_user(data):

#     user = await users_collection.find_one(
#         {
#             "email": data.email.lower()
#         }
#     )

#     if user is None:

#         raise HTTPException(
#             status_code=401,
#             detail={
#                 "success": False,
#                 "error_code": 401,
#                 "message": "Invalid email or password"
#             }
#         )

#     if not verify_password(
#         data.password,
#         user["password_hash"]
#     ):

#         raise HTTPException(
#             status_code=401,
#             detail={
#                 "success": False,
#                 "error_code": 401,
#                 "message": "Invalid email or password"
#             }
#         )

#     if not user.get("is_active", True):

#         raise HTTPException(
#             status_code=403,
#             detail={
#                 "success": False,
#                 "error_code": 403,
#                 "message": "User account is inactive"
#             }
#         )

#     user_id = str(user["_id"])

#     access_token = create_access_token(
#         user_id
#     )

#     refresh_token = create_refresh_token()

#     refresh_document = {
#         "user_id": user["_id"],
#         "token_hash": hash_refresh_token(refresh_token),
#         "expires_at": create_refresh_expiry(),
#         "created_at": datetime.now(timezone.utc),
#         "revoked": False
#     }

#     await refresh_tokens_collection.insert_one(
#         refresh_document
#     )

#     return {
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer"
#     }


# async def refresh_access_token(refresh_token: str):

#     token_hash = hash_refresh_token(
#         refresh_token
#     )

#     stored_token = await refresh_tokens_collection.find_one(
#         {
#             "token_hash": token_hash,
#             "revoked": False
#         }
#     )

#     if stored_token is None:

#         raise HTTPException(
#             status_code=401,
#             detail={
#                 "success": False,
#                 "error_code": 401,
#                 "message": "Invalid refresh token"
#             }
#         )

#     # Get expiration time from MongoDB
#     expires_at = stored_token["expires_at"]

#     # MongoDB may return a timezone-naive datetime.
#     # Convert it to timezone-aware UTC datetime.
#     if expires_at.tzinfo is None:
#         expires_at = expires_at.replace(
#             tzinfo=timezone.utc
#         )

#     # Check refresh token expiration
#     if expires_at <= datetime.now(timezone.utc):

#         raise HTTPException(
#             status_code=401,
#             detail={
#                 "success": False,
#                 "error_code": 401,
#                 "message": "Refresh token has expired"
#             }
#         )

#     user = await users_collection.find_one(
#         {
#             "_id": stored_token["user_id"]
#         }
#     )

#     if user is None:

#         raise HTTPException(
#             status_code=404,
#             detail={
#                 "success": False,
#                 "error_code": 404,
#                 "message": "User not found"
#             }
#         )

#     if not user.get("is_active", True):

#         raise HTTPException(
#             status_code=403,
#             detail={
#                 "success": False,
#                 "error_code": 403,
#                 "message": "User account is inactive"
#             }
#         )

#     new_access_token = create_access_token(
#         str(user["_id"])
#     )

#     return {
#         "access_token": new_access_token,
#         "token_type": "bearer"
#     }


# async def logout_user(refresh_token: str):

#     token_hash = hash_refresh_token(
#         refresh_token
#     )

#     result = await refresh_tokens_collection.update_one(
#         {
#             "token_hash": token_hash,
#             "revoked": False
#         },
#         {
#             "$set": {
#                 "revoked": True,
#                 "revoked_at": datetime.now(timezone.utc)
#             }
#         }
#     )

#     if result.matched_count == 0:

#         raise HTTPException(
#             status_code=401,
#             detail={
#                 "success": False,
#                 "error_code": 401,
#                 "message": "Invalid refresh token"
#             }
#         )

#     return True

from datetime import datetime, timezone

from fastapi import HTTPException
from passlib.context import CryptContext

from app.auth.jwt_handler import (
    create_access_token,
    create_refresh_expiry,
    create_refresh_token,
    hash_refresh_token
)

from app.database.mongodb import (
    users_collection,
    refresh_tokens_collection
)


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# ============================================================
# REGISTER USER
# ============================================================

async def register_user(data):

    # Check duplicate email
    existing_user = await users_collection.find_one(
        {
            "email": data.email.lower()
        }
    )

    if existing_user:

        raise HTTPException(
            status_code=409,
            detail={
                "success": False,
                "error_code": 409,
                "message": "Email already registered"
            }
        )

    # Validate role
    if data.role not in ["user", "admin"]:

        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "error_code": 422,
                "message": "Invalid role"
            }
        )

    # Create MongoDB document
    user_document = {
        "username": data.username.strip(),
        "email": data.email.lower(),
        "password_hash": hash_password(data.password),

        # IMPORTANT
        # Role comes from UserRegister
        "role": data.role,

        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    }

    # Insert user
    result = await users_collection.insert_one(
        user_document
    )

    # Return safe response
    return {
        "id": str(result.inserted_id),
        "username": user_document["username"],
        "email": user_document["email"],
        "role": user_document["role"],
        "is_active": user_document["is_active"]
    }


# ============================================================
# LOGIN USER
# ============================================================

async def login_user(data):

    # Find user by email
    user = await users_collection.find_one(
        {
            "email": data.email.lower()
        }
    )

    if user is None:

        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error_code": 401,
                "message": "Invalid email or password"
            }
        )

    # Verify password
    if not verify_password(
        data.password,
        user["password_hash"]
    ):

        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error_code": 401,
                "message": "Invalid email or password"
            }
        )

    # Check active status
    if not user.get("is_active", True):

        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "error_code": 403,
                "message": "User account is inactive"
            }
        )

    # Get MongoDB user ID
    user_id = str(user["_id"])

    # Create access token
    access_token = create_access_token(
        user_id
    )

    # Create refresh token
    refresh_token = create_refresh_token()

    # Store only hashed refresh token
    refresh_document = {
        "user_id": user["_id"],
        "token_hash": hash_refresh_token(
            refresh_token
        ),
        "expires_at": create_refresh_expiry(),
        "created_at": datetime.now(timezone.utc),
        "revoked": False
    }

    await refresh_tokens_collection.insert_one(
        refresh_document
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# ============================================================
# REFRESH ACCESS TOKEN
# ============================================================

async def refresh_access_token(
    refresh_token: str
):

    # Hash received refresh token
    token_hash = hash_refresh_token(
        refresh_token
    )

    # Find valid stored session
    stored_token = await refresh_tokens_collection.find_one(
        {
            "token_hash": token_hash,
            "revoked": False
        }
    )

    if stored_token is None:

        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error_code": 401,
                "message": "Invalid refresh token"
            }
        )

    # Get expiration
    expires_at = stored_token["expires_at"]

    # Convert naive datetime to UTC
    if expires_at.tzinfo is None:

        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    # Check expiration
    if expires_at <= datetime.now(timezone.utc):

        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error_code": 401,
                "message": "Refresh token has expired"
            }
        )

    # Find associated user
    user = await users_collection.find_one(
        {
            "_id": stored_token["user_id"]
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

    # Check user active status
    if not user.get("is_active", True):

        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "error_code": 403,
                "message": "User account is inactive"
            }
        )

    # Create new access token
    new_access_token = create_access_token(
        str(user["_id"])
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }


# ============================================================
# LOGOUT USER
# ============================================================

async def logout_user(
    refresh_token: str
):

    # Hash refresh token
    token_hash = hash_refresh_token(
        refresh_token
    )

    # Revoke refresh token
    result = await refresh_tokens_collection.update_one(
        {
            "token_hash": token_hash,
            "revoked": False
        },
        {
            "$set": {
                "revoked": True,
                "revoked_at": datetime.now(timezone.utc)
            }
        }
    )

    # Token not found / already revoked
    if result.matched_count == 0:

        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error_code": 401,
                "message": "Invalid refresh token"
            }
        )

    return True