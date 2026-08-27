from bson import ObjectId
from fastapi import HTTPException, status

from app.database.mongodb import users_collection
from app.models.user import UserUpdate


async def update_current_user(
    user_id: str,
    data: UserUpdate
):

    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID",
        )

    update_data = data.model_dump(
        exclude_none=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update data provided",
        )

    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data},
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user = await users_collection.find_one(
        {"_id": ObjectId(user_id)}
    )

    user["id"] = str(user["_id"])

    user.pop("_id", None)
    user.pop("password", None)

    return user


async def get_all_users():

    cursor = users_collection.find(
        {},
        {
            "password": 0,
        }
    )

    users = []

    async for user in cursor:
        user["id"] = str(user["_id"])
        user.pop("_id", None)
        users.append(user)

    return users