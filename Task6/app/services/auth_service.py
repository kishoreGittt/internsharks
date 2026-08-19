from passlib.context import CryptContext
from pymongo.errors import DuplicateKeyError

from app.database.connection import users_collection


# ============================================================
# Password Hashing Configuration
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
# Register User
# ============================================================

async def register_user(
    username: str,
    email: str,
    password: str
):

    # Convert email to lowercase
    email = email.lower().strip()

    # --------------------------------------------------------
    # Check if email already exists
    # --------------------------------------------------------

    existing_user = await users_collection.find_one(
        {"email": email}
    )

    if existing_user:

        return {
            "success": False,
            "error_code": "USER_ALREADY_EXISTS",
            "message": "Email is already registered",
            "data": None
        }

    # --------------------------------------------------------
    # Hash password
    # --------------------------------------------------------

    password_hash = hash_password(password)

    # --------------------------------------------------------
    # Create user document
    # --------------------------------------------------------

    user_document = {
        "username": username.strip(),
        "email": email,
        "password_hash": password_hash
    }

    # --------------------------------------------------------
    # Insert into MongoDB
    # --------------------------------------------------------

    try:

        result = await users_collection.insert_one(
            user_document
        )

    except DuplicateKeyError:

        return {
            "success": False,
            "error_code": "USER_ALREADY_EXISTS",
            "message": "Email is already registered",
            "data": None
        }

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "success": True,
        "error_code": None,
        "message": "User registered successfully",
        "data": {
            "id": str(result.inserted_id),
            "username": username.strip(),
            "email": email
        }
    }


# ============================================================
# Login User
# ============================================================

async def login_user(
    email: str,
    password: str
):

    email = email.lower().strip()

    # --------------------------------------------------------
    # Find user
    # --------------------------------------------------------

    user = await users_collection.find_one(
        {"email": email}
    )

    # --------------------------------------------------------
    # User not found
    # --------------------------------------------------------

    if not user:

        return {
            "success": False,
            "error_code": "INVALID_CREDENTIALS",
            "message": "Invalid email or password",
            "data": None
        }

    # --------------------------------------------------------
    # Get stored password hash
    # --------------------------------------------------------

    stored_password_hash = user.get("password_hash")

    if not stored_password_hash:

        return {
            "success": False,
            "error_code": "INVALID_USER_DATA",
            "message": "User authentication data is invalid",
            "data": None
        }

    # --------------------------------------------------------
    # Verify password
    # --------------------------------------------------------

    password_is_valid = verify_password(
        password,
        stored_password_hash
    )

    if not password_is_valid:

        return {
            "success": False,
            "error_code": "INVALID_CREDENTIALS",
            "message": "Invalid email or password",
            "data": None
        }

    # --------------------------------------------------------
    # Successful login
    # --------------------------------------------------------

    return {
        "success": True,
        "error_code": None,
        "message": "Login successful",
        "data": {
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"]
        }
    }


# ============================================================
# Get User Profile
# ============================================================

async def get_user_profile(email: str):

    email = email.lower().strip()

    # --------------------------------------------------------
    # Find user
    # --------------------------------------------------------

    user = await users_collection.find_one(
        {"email": email}
    )

    if not user:

        return {
            "success": False,
            "error_code": "USER_NOT_FOUND",
            "message": "User profile not found",
            "data": None
        }

    # --------------------------------------------------------
    # Return only safe information
    # --------------------------------------------------------

    return {
        "success": True,
        "error_code": None,
        "message": "User profile retrieved successfully",
        "data": {
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"]
        }
    }