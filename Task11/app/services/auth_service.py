from datetime import datetime, timezone

from fastapi import HTTPException
from passlib.context import CryptContext

from app.auth.jwt_handler import (
    create_access_token,
    create_refresh_expiry,
    create_refresh_token,
    hash_refresh_token,
)

from app.database.mongodb import (
    users_collection,
    refresh_tokens_collection,
)


# ============================================================
# PASSWORD HASHING
# ============================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


# ============================================================
# HASH PASSWORD
# ============================================================

def hash_password(password: str) -> str:

    return pwd_context.hash(password)


# ============================================================
# VERIFY PASSWORD
# ============================================================

def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:

    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


# ============================================================
# REGISTER USER
# ============================================================

async def register_user(data):

    # --------------------------------------------------------
    # Check duplicate email
    # --------------------------------------------------------

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
                "status_code": 409,
                "error": "CONFLICT",
                "message": "Email already registered",
            },
        )

    # --------------------------------------------------------
    # Validate role
    # --------------------------------------------------------

    if data.role not in ["user", "admin"]:

        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "status_code": 422,
                "error": "VALIDATION_ERROR",
                "message": "Role must be either user or admin",
            },
        )

    # --------------------------------------------------------
    # Create MongoDB user document
    # --------------------------------------------------------

    user_document = {

        "username": data.username.strip(),

        "email": data.email.lower(),

        "password_hash": hash_password(
            data.password
        ),

        "full_name": data.full_name.strip(),

        "phone": data.phone,

        "department": data.department,

        # Role selected during registration
        "role": data.role,

        "is_active": True,

        "created_at": datetime.now(timezone.utc),
    }

    # --------------------------------------------------------
    # Insert user into MongoDB
    # --------------------------------------------------------

    result = await users_collection.insert_one(
        user_document
    )

    # --------------------------------------------------------
    # Return safe response
    # --------------------------------------------------------
    # NEVER return password_hash
    # --------------------------------------------------------

    return {

        "id": str(result.inserted_id),

        "username": user_document["username"],

        "email": user_document["email"],

        "full_name": user_document["full_name"],

        "phone": user_document["phone"],

        "department": user_document["department"],

        "role": user_document["role"],

        "is_active": user_document["is_active"],
    }


# ============================================================
# LOGIN USER
# ============================================================

async def login_user(data):

    # --------------------------------------------------------
    # Find user
    # --------------------------------------------------------

    user = await users_collection.find_one(
        {
            "email": data.email.lower()
        }
    )

    # --------------------------------------------------------
    # User not found
    # --------------------------------------------------------

    if user is None:

        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "status_code": 401,
                "error": "UNAUTHORIZED",
                "message": "Invalid email or password",
            },
        )

    # --------------------------------------------------------
    # Verify password
    # --------------------------------------------------------

    password_valid = verify_password(
        data.password,
        user["password_hash"],
    )

    if not password_valid:

        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "status_code": 401,
                "error": "UNAUTHORIZED",
                "message": "Invalid email or password",
            },
        )

    # --------------------------------------------------------
    # Check active status
    # --------------------------------------------------------

    if not user.get("is_active", True):

        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "status_code": 403,
                "error": "FORBIDDEN",
                "message": "User account is inactive",
            },
        )

    # --------------------------------------------------------
    # Get user ID
    # --------------------------------------------------------

    user_id = str(
        user["_id"]
    )

    # --------------------------------------------------------
    # Get role from MongoDB
    # --------------------------------------------------------

    role = user.get(
        "role",
        "user"
    )

    # --------------------------------------------------------
    # Create access token
    # --------------------------------------------------------

    access_token = create_access_token(
        user_id=user_id,
        role=role,
    )

    # --------------------------------------------------------
    # Create refresh token
    # --------------------------------------------------------

    refresh_token = create_refresh_token()

    # --------------------------------------------------------
    # Store hashed refresh token
    # --------------------------------------------------------

    refresh_document = {

        "user_id": user["_id"],

        "token_hash": hash_refresh_token(
            refresh_token
        ),

        "expires_at": create_refresh_expiry(),

        "created_at": datetime.now(timezone.utc),

        "revoked": False,
    }

    await refresh_tokens_collection.insert_one(
        refresh_document
    )

    # --------------------------------------------------------
    # Return tokens
    # --------------------------------------------------------

    return {

        "access_token": access_token,

        "refresh_token": refresh_token,

        "token_type": "bearer",
    }


# ============================================================
# REFRESH ACCESS TOKEN
# ============================================================

async def refresh_access_token(
    refresh_token: str,
):

    # --------------------------------------------------------
    # Hash received refresh token
    # --------------------------------------------------------

    token_hash = hash_refresh_token(
        refresh_token
    )

    # --------------------------------------------------------
    # Find refresh token
    # --------------------------------------------------------

    stored_token = await refresh_tokens_collection.find_one(
        {
            "token_hash": token_hash,
            "revoked": False,
        }
    )

    if stored_token is None:

        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "status_code": 401,
                "error": "UNAUTHORIZED",
                "message": "Invalid refresh token",
            },
        )

    # --------------------------------------------------------
    # Get expiration
    # --------------------------------------------------------

    expires_at = stored_token["expires_at"]

    # MongoDB can return a naive datetime
    if expires_at.tzinfo is None:

        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    # --------------------------------------------------------
    # Check expiration
    # --------------------------------------------------------

    if expires_at <= datetime.now(timezone.utc):

        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "status_code": 401,
                "error": "UNAUTHORIZED",
                "message": "Refresh token has expired",
            },
        )

    # --------------------------------------------------------
    # Find associated user
    # --------------------------------------------------------

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
                "status_code": 404,
                "error": "NOT_FOUND",
                "message": "User not found",
            },
        )

    # --------------------------------------------------------
    # Check active status
    # --------------------------------------------------------

    if not user.get("is_active", True):

        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "status_code": 403,
                "error": "FORBIDDEN",
                "message": "User account is inactive",
            },
        )

    # --------------------------------------------------------
    # Get CURRENT role from MongoDB
    # --------------------------------------------------------

    role = user.get(
        "role",
        "user"
    )

    # --------------------------------------------------------
    # Create new access token
    # --------------------------------------------------------

    new_access_token = create_access_token(
        user_id=str(user["_id"]),
        role=role,
    )

    return {

        "access_token": new_access_token,

        "token_type": "bearer",
    }


# ============================================================
# LOGOUT USER
# ============================================================

async def logout_user(
    refresh_token: str,
):

    # --------------------------------------------------------
    # Hash refresh token
    # --------------------------------------------------------

    token_hash = hash_refresh_token(
        refresh_token
    )

    # --------------------------------------------------------
    # Revoke refresh token
    # --------------------------------------------------------

    result = await refresh_tokens_collection.update_one(

        {
            "token_hash": token_hash,
            "revoked": False,
        },

        {
            "$set": {
                "revoked": True,
                "revoked_at": datetime.now(timezone.utc),
            }
        },
    )

    # --------------------------------------------------------
    # Token not found / already revoked
    # --------------------------------------------------------

    if result.matched_count == 0:

        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "status_code": 401,
                "error": "UNAUTHORIZED",
                "message": "Invalid refresh token",
            },
        )

    return True