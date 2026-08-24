from bson import ObjectId
from passlib.context import CryptContext

from app.database.mongodb import (
    users_collection,
    refresh_sessions_collection
)

from app.models.refresh_session import (
    create_refresh_session_document
)

from app.services.token_service import (
    create_access_token,
    create_refresh_token,
    hash_jti
)


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


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


async def register_user(
    username: str,
    email: str,
    password: str,
    full_name: str,
    phone: str
):

    existing_user = await users_collection.find_one(
        {"email": email}
    )

    if existing_user:
        return None

    user = {
        "username": username,
        "email": email,
        "password": hash_password(password),
        "full_name": full_name,
        "phone": phone,
        "role": "user",
        "is_active": True
    }

    result = await users_collection.insert_one(user)

    user["id"] = str(result.inserted_id)

    return user


async def authenticate_user(
    email: str,
    password: str
):

    user = await users_collection.find_one(
        {"email": email}
    )

    if not user:
        return None, "USER_NOT_FOUND"

    if not verify_password(
        password,
        user["password"]
    ):
        return None, "INVALID_PASSWORD"

    if not user.get("is_active", True):
        return None, "USER_INACTIVE"

    return user, None


async def create_login_tokens(user: dict):

    user_id = str(user["_id"])

    access_token = create_access_token(
        user_id
    )

    refresh_token, jti, expires_at = create_refresh_token(
        user_id
    )

    jti_hash = hash_jti(jti)

    session = create_refresh_session_document(
        user_id=user_id,
        jti_hash=jti_hash,
        expires_at=expires_at
    )

    await refresh_sessions_collection.insert_one(
        session
    )

    return access_token, refresh_token


async def get_user_by_id(user_id: str):

    try:
        object_id = ObjectId(user_id)
    except Exception:
        return None

    return await users_collection.find_one(
        {"_id": object_id}
    )


async def get_refresh_session(
    user_id: str,
    jti_hash: str
):

    return await refresh_sessions_collection.find_one(
        {
            "user_id": user_id,
            "jti_hash": jti_hash
        }
    )


async def revoke_refresh_session(
    user_id: str,
    jti_hash: str
):

    result = await refresh_sessions_collection.update_one(
        {
            "user_id": user_id,
            "jti_hash": jti_hash,
            "revoked": False
        },
        {
            "$set": {
                "revoked": True
            }
        }
    )

    return result.modified_count > 0