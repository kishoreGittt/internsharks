from bson import ObjectId

from app.database.mongodb import users_collection


def serialize_user(user):

    return {
        "username": user["username"],
        "email": user["email"],
        "full_name": user["full_name"],
        "phone": user["phone"],
        "department": user["department"],
        "role": user["role"],
        "is_active": user["is_active"]
    }


async def get_user_by_id(user_id: str):

    if not ObjectId.is_valid(user_id):

        return None

    user = await users_collection.find_one(
        {"_id": ObjectId(user_id)}
    )

    return user


async def update_own_profile(
    current_user,
    update_data
):

    updates = update_data.model_dump(
        exclude_unset=True
    )

    if not updates:

        return current_user, False, "NO_UPDATE_FIELDS"


    if "username" in updates:

        existing_username = await users_collection.find_one(
            {
                "username": updates["username"],
                "email": {
                    "$ne": current_user["email"]
                }
            }
        )

        if existing_username:

            return None, False, "USERNAME_EXISTS"


    await users_collection.update_one(
        {"email": current_user["email"]},
        {"$set": updates}
    )

    updated_user = await users_collection.find_one(
        {"email": current_user["email"]}
    )

    return updated_user, True, None


async def get_all_users(
    role=None,
    department=None,
    is_active=None
):

    query = {}

    if role is not None:

        query["role"] = role

    if department is not None:

        query["department"] = department

    if is_active is not None:

        query["is_active"] = is_active


    cursor = users_collection.find(query)

    users = []

    async for user in cursor:

        users.append(
            serialize_user(user)
        )

    return users


async def update_user_role(
    user_id: str,
    role: str
):

    if not ObjectId.is_valid(user_id):

        return None

    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "role": role
            }
        }
    )

    if result.matched_count == 0:

        return None

    return await get_user_by_id(user_id)


async def update_user_status(
    user_id: str,
    is_active: bool
):

    if not ObjectId.is_valid(user_id):

        return None

    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "is_active": is_active
            }
        }
    )

    if result.matched_count == 0:

        return None

    return await get_user_by_id(user_id)


async def delete_user(user_id: str):

    if not ObjectId.is_valid(user_id):

        return False

    result = await users_collection.delete_one(
        {"_id": ObjectId(user_id)}
    )

    return result.deleted_count > 0