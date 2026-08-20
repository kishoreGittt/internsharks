from fastapi import APIRouter, HTTPException, status

from app.models.auth import (
    RegisterRequest,
    LoginRequest
)

from app.services.auth_service import (
    register_user,
    authenticate_user
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
async def register(data: RegisterRequest):

    user, error = await register_user(data)


    if error == "EMAIL_EXISTS":

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "success": False,
                "message": "Email already registered",
                "error_code": "EMAIL_ALREADY_EXISTS"
            }
        )


    if error == "USERNAME_EXISTS":

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "success": False,
                "message": "Username already exists",
                "error_code": "USERNAME_ALREADY_EXISTS"
            }
        )


    return {
        "success": True,
        "message": "User registered successfully",
        "data": {
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "phone": user["phone"],
            "department": user["department"],
            "role": user["role"],
            "is_active": user["is_active"]
        }
    }


# ============================================================
# LOGIN
# ============================================================

@router.post("/login")
async def login(data: LoginRequest):

    token, error = await authenticate_user(
        data.email,
        data.password
    )


    if error == "INVALID_CREDENTIALS":

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "message": "Invalid email or password",
                "error_code": "INVALID_CREDENTIALS"
            }
        )


    if error == "ACCOUNT_INACTIVE":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "message": "Account is deactivated",
                "error_code": "ACCOUNT_INACTIVE"
            }
        )


    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "access_token": token,
            "token_type": "bearer"
        }
    }