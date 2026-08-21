from passlib.context import CryptContext

from app.database.mongodb import (
    users_collection
)

from app.auth.jwt_handler import (
    create_access_token
)


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# ============================================================
# HASH PASSWORD
# ============================================================

def hash_password(
    password: str
):

    return pwd_context.hash(
        password
    )


# ============================================================
# VERIFY PASSWORD
# ============================================================

def verify_password(
    plain_password: str,
    hashed_password: str
):

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# ============================================================
# NORMAL USER REGISTER
# ============================================================

async def register_user(
    data
):

    existing_email = await users_collection.find_one(
        {
            "email": data.email
        }
    )

    if existing_email:

        return None, "EMAIL_EXISTS"


    existing_username = await users_collection.find_one(
        {
            "username": data.username
        }
    )

    if existing_username:

        return None, "USERNAME_EXISTS"


    user = {

        "username": data.username,

        "email": data.email,

        "password": hash_password(
            data.password
        ),

        "full_name": data.full_name,

        "phone": data.phone,

        "department": data.department,

        # ALWAYS USER
        "role": "user",

        "is_active": True
    }


    result = await users_collection.insert_one(
        user
    )

    user["_id"] = result.inserted_id

    return user, None


# ============================================================
# ADMIN REGISTER
# ============================================================

async def register_admin(
    data
):

    existing_email = await users_collection.find_one(
        {
            "email": data.email
        }
    )

    if existing_email:

        return None, "EMAIL_EXISTS"


    existing_username = await users_collection.find_one(
        {
            "username": data.username
        }
    )

    if existing_username:

        return None, "USERNAME_EXISTS"


    admin = {

        "username": data.username,

        "email": data.email,

        "password": hash_password(
            data.password
        ),

        "full_name": data.full_name,

        "phone": data.phone,

        "department": data.department,

        # ADMIN
        "role": "admin",

        "is_active": True
    }


    result = await users_collection.insert_one(
        admin
    )

    admin["_id"] = result.inserted_id

    return admin, None


# ============================================================
# LOGIN
# ============================================================

async def authenticate_user(
    email: str,
    password: str
):

    user = await users_collection.find_one(
        {
            "email": email
        }
    )


    if not user:

        return None, "INVALID_CREDENTIALS"


    if not user.get(
        "is_active",
        True
    ):

        return None, "ACCOUNT_INACTIVE"


    if not verify_password(
        password,
        user["password"]
    ):

        return None, "INVALID_CREDENTIALS"


    token = create_access_token(
        user["email"]
    )

    return token, None