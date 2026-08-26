from fastapi import HTTPException, status

from app.database.mongodb import users_collection


def serialize_user(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "full_name": user.get("full_name"),
        "role": user["role"],
        "is_active": user["is_active"],
        "created_at": user["created_at"]
    }


async def get_user_profile(user: dict):
    return serialize_user(user)


async def get_all_users():
    cursor = users_collection.find(
        {},
        {
            "password_hash": 0
        }
    ).sort(
        "created_at",
        -1
    )

    users = []

    async for user in cursor:
        users.append(
            serialize_user(user)
        )

    return users


async def get_user_by_id(user_id):
    from app.utils.object_id import to_object_id

    try:
        object_id = to_object_id(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "message": "Invalid user ID",
                "error_code": "INVALID_USER_ID"
            }
        )

    user = await users_collection.find_one({
        "_id": object_id
    })

    return user