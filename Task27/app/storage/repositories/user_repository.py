from app.storage.mongodb import (
    users_collection
)


async def create_user(
    user: dict
):

    await users_collection.insert_one(
        user
    )

    return user


async def get_user_by_email(
    email: str
):

    return await users_collection.find_one(
        {
            "email": email
        }
    )


async def get_user_by_id(
    user_id: str
):

    return await users_collection.find_one(
        {
            "user_id": user_id
        },
        {
            "_id": 0,
            "password_hash": 0
        }
    )