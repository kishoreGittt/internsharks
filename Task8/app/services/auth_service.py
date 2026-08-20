from passlib.context import CryptContext

from app.database.mongodb import users_collection
from app.auth.jwt_handler import create_access_token


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# ============================================================
# Password Hashing
# ============================================================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# ============================================================
# Password Verification
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
# Register User
# ============================================================

async def register_user(data):

    # Check duplicate email
    existing_email = await users_collection.find_one(
        {
            "email": data.email
        }
    )

    if existing_email:
        return None, "EMAIL_EXISTS"


    # Check duplicate username
    existing_username = await users_collection.find_one(
        {
            "username": data.username
        }
    )

    if existing_username:
        return None, "USERNAME_EXISTS"


    # Hash password
    hashed_password = hash_password(
        data.password
    )


    # Create user document
    user_document = {
        "username": data.username,
        "email": data.email,
        "password": hashed_password,
        "full_name": data.full_name,
        "phone": data.phone,
        "department": data.department,

        # IMPORTANT
        # User can NEVER choose these during registration
        "role": "user",
        "is_active": True
    }


    # Insert into MongoDB
    result = await users_collection.insert_one(
        user_document
    )


    user_document["_id"] = result.inserted_id

    return user_document, None


# ============================================================
# Login / Authentication
# ============================================================

async def authenticate_user(
    email: str,
    password: str
):

    # Find user using email
    user = await users_collection.find_one(
        {
            "email": email
        }
    )


    # User does not exist
    if not user:

        return None, "INVALID_CREDENTIALS"


    # Check account status
    if not user.get(
        "is_active",
        True
    ):

        return None, "ACCOUNT_INACTIVE"


    # Verify password
    password_valid = verify_password(
        password,
        user["password"]
    )


    if not password_valid:

        return None, "INVALID_CREDENTIALS"


    # Generate JWT
    token = create_access_token(
        user["email"]
    )


    return token, None