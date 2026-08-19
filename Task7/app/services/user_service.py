from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from passlib.context import CryptContext

from app.database.mongodb import users_collection


# ============================================================
# Password Hashing
# ============================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# ============================================================
# Hash Password
# ============================================================

def hash_password(password: str) -> str:

    return pwd_context.hash(password)


# ============================================================
# Verify Password
# ============================================================

def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# ============================================================
# Find User By Email
# ============================================================

async def find_user_by_email(
    email: str
) -> Optional[dict]:

    return await users_collection.find_one(
        {
            "email": email.lower()
        }
    )


# ============================================================
# Find User By ID
# ============================================================

async def find_user_by_id(
    user_id: str
) -> Optional[dict]:

    try:

        object_id = ObjectId(user_id)

    except InvalidId:

        return None

    return await users_collection.find_one(
        {
            "_id": object_id
        }
    )


# ============================================================
# Create User
# ============================================================

async def create_user(
    username: str,
    email: str,
    password: str
) -> dict:

    password_hash = hash_password(password)

    user_document = {
        "username": username,
        "email": email.lower(),
        "password_hash": password_hash
    }

    result = await users_collection.insert_one(
        user_document
    )

    user_document["_id"] = result.inserted_id

    return user_document