from bson import ObjectId
from bson.errors import InvalidId

from app.database.mongodb import (
    users_collection
)


# ============================================================
# SERIALIZE USER
# ============================================================

def serialize_user(user):

    return {

        "id": str(
            user["_id"]
        ),

        "username": user.get(
            "username"
        ),

        "email": user.get(
            "email"
        ),

        "full_name": user.get(
            "full_name"
        ),

        "phone": user.get(
            "phone"
        ),

        "department": user.get(
            "department"
        ),

        "role": user.get(
            "role",
            "user"
        ),

        "is_active": user.get(
            "is_active",
            True
        )
    }


# ============================================================
# GET USER BY ID
# ============================================================

async def get_user_by_id(user_id: str):

    try:

        object_id = ObjectId(
            user_id
        )

    except InvalidId:

        return None, "INVALID_ID"


    user = await users_collection.find_one(
        {
            "_id": object_id
        }
    )


    if not user:

        return None, "USER_NOT_FOUND"


    return user, None


# ============================================================
# UPDATE OWN PROFILE
# ============================================================

async def update_own_profile(
    current_user,
    data
):

    update_data = data.model_dump(
        exclude_unset=True
    )


    # Nothing to update
    if not update_data:

        return current_user, None


    # --------------------------------------------------------
    # Check username uniqueness
    # --------------------------------------------------------

    if "username" in update_data:

        existing = await users_collection.find_one(

            {
                "username": update_data["username"],

                "_id": {
                    "$ne": current_user["_id"]
                }
            }
        )


        if existing:

            return None, "USERNAME_EXISTS"


    # --------------------------------------------------------
    # Update
    # --------------------------------------------------------

    await users_collection.update_one(

        {
            "_id": current_user["_id"]
        },

        {
            "$set": update_data
        }
    )


    # --------------------------------------------------------
    # Get updated user
    # --------------------------------------------------------

    updated_user = await users_collection.find_one(

        {
            "_id": current_user["_id"]
        }
    )


    return updated_user, None


# ============================================================
# GET ALL USERS
# ============================================================

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


    users = []


    cursor = users_collection.find(
        query
    )


    async for user in cursor:

        users.append(
            serialize_user(user)
        )


    return users


# ============================================================
# CHANGE ROLE
# ============================================================

async def change_user_role(
    user_id: str,
    role: str
):

    user, error = await get_user_by_id(
        user_id
    )


    if error:

        return None, error


    await users_collection.update_one(

        {
            "_id": user["_id"]
        },

        {
            "$set": {
                "role": role
            }
        }
    )


    updated_user = await users_collection.find_one(

        {
            "_id": user["_id"]
        }
    )


    return updated_user, None


# ============================================================
# CHANGE STATUS
# ============================================================

async def change_user_status(
    user_id: str,
    is_active: bool
):

    user, error = await get_user_by_id(
        user_id
    )


    if error:

        return None, error


    await users_collection.update_one(

        {
            "_id": user["_id"]
        },

        {
            "$set": {
                "is_active": is_active
            }
        }
    )


    updated_user = await users_collection.find_one(

        {
            "_id": user["_id"]
        }
    )


    return updated_user, None


# ============================================================
# DELETE USER
# ============================================================

async def delete_user(
    user_id: str
):

    user, error = await get_user_by_id(
        user_id
    )


    if error:

        return None, error


    await users_collection.delete_one(

        {
            "_id": user["_id"]
        }
    )


    return user, None