from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr

from app.auth.dependencies import get_current_user
from app.auth.jwt import create_access_token
from app.auth.security import hash_password, verify_password
from app.storage.mongodb import users_collection


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

security = HTTPBearer()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):

    existing_user = await users_collection.find_one(
        {"email": request.email}
    )

    if existing_user:
        return {
            "success": False,
            "status_code": 409,
            "error": "USER_EXISTS",
            "message": "User already exists"
        }

    user = {
        "email": request.email,
        "name": request.name,
        "password_hash": hash_password(request.password),
        "role": "user"
    }

    result = await users_collection.insert_one(user)

    return {
        "success": True,
        "status_code": 201,
        "data": {
            "user_id": str(result.inserted_id),
            "email": request.email,
            "name": request.name,
            "role": "user"
        }
    }


@router.post("/login")
async def login(request: LoginRequest):

    user = await users_collection.find_one(
        {"email": request.email}
    )

    if not user:
        return {
            "success": False,
            "status_code": 401,
            "error": "INVALID_CREDENTIALS",
            "message": "Invalid email or password"
        }

    if not verify_password(
        request.password,
        user.get("password_hash", "")
    ):
        return {
            "success": False,
            "status_code": 401,
            "error": "INVALID_CREDENTIALS",
            "message": "Invalid email or password"
        }

    token_data = {
        "user_id": str(user["_id"]),
        "email": user["email"],
        "role": user.get("role", "user")
    }

    access_token = create_access_token(token_data)

    return {
        "success": True,
        "status_code": 200,
        "data": {
            "access_token": access_token,
            "token_type": "bearer"
        }
    }


# ---------------------------------------------------------
# CURRENT USER
# ---------------------------------------------------------

@router.get("/me")
async def get_me(
    current_user: dict = Depends(get_current_user)
):

    return {
        "success": True,
        "status_code": 200,
        "data": {
            "user_id": current_user.get("user_id"),
            "email": current_user.get("email"),
            "name": current_user.get("name"),
            "role": current_user.get("role", "user")
        }
    }