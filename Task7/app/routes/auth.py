from fastapi import APIRouter, HTTPException, status

from passlib.context import CryptContext

from app.database.mongodb import users_collection

from app.models.user import (
    UserCreate,
    UserLogin
)

from app.auth.jwt_handler import (
    create_access_token
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ============================================================
# Password Hashing
# ============================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
async def register_user(user: UserCreate):

    try:

        # Check existing email

        existing_user = await users_collection.find_one(
            {
                "email": user.email
            }
        )

        if existing_user:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "success": False,
                    "error_code": "USER_ALREADY_EXISTS",
                    "message": "A user with this email already exists"
                }
            )

        # Hash password

        hashed_password = pwd_context.hash(
            user.password
        )

        # Create MongoDB document

        new_user = {
            "username": user.username,
            "email": user.email,
            "password": hashed_password
        }

        # Insert

        result = await users_collection.insert_one(
            new_user
        )

        # Structured response

        return {
            "success": True,
            "message": "User registered successfully",
            "data": {
                "id": str(result.inserted_id),
                "username": user.username,
                "email": user.email
            }
        }

    except HTTPException:

        raise

    except Exception:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error_code": "REGISTRATION_FAILED",
                "message": "An error occurred while registering the user"
            }
        )


# ============================================================
# LOGIN
# ============================================================

@router.post("/login")
async def login_user(user: UserLogin):

    try:

        # Find user

        existing_user = await users_collection.find_one(
            {
                "email": user.email
            }
        )

        # User does not exist

        if not existing_user:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "success": False,
                    "error_code": "INVALID_CREDENTIALS",
                    "message": "Invalid email or password"
                }
            )

        # Verify password

        password_valid = pwd_context.verify(
            user.password,
            existing_user["password"]
        )

        if not password_valid:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "success": False,
                    "error_code": "INVALID_CREDENTIALS",
                    "message": "Invalid email or password"
                }
            )

        # Create JWT

        access_token = create_access_token(
            {
                "sub": str(existing_user["_id"])
            }
        )

        # Return token

        return {
            "success": True,
            "message": "Login successful",
            "data": {
                "access_token": access_token,
                "token_type": "bearer"
            }
        }

    except HTTPException:

        raise

    except Exception:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error_code": "LOGIN_FAILED",
                "message": "An error occurred while logging in"
            }
        )