from fastapi import (
    APIRouter,
    HTTPException,
    status
)

from app.models.auth import (
    RegisterRequest,
    AdminRegisterRequest,
    LoginRequest
)

from app.services.auth_service import (
    register_user,
    register_admin,
    authenticate_user
)

from app.config import ADMIN_SETUP_KEY


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ============================================================
# NORMAL USER REGISTER
# ============================================================

@router.post(
    "/register",
    status_code=201
)
async def register(
    data: RegisterRequest
):

    user, error = await register_user(
        data
    )


    if error == "EMAIL_EXISTS":

        raise HTTPException(
            status_code=409,
            detail={
                "success": False,
                "message": "Email already registered",
                "error_code": "EMAIL_ALREADY_EXISTS"
            }
        )


    if error == "USERNAME_EXISTS":

        raise HTTPException(
            status_code=409,
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

            "id": str(
                user["_id"]
            ),

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
# ADMIN REGISTER
# ============================================================

@router.post(
    "/register-admin",
    status_code=201
)
async def register_admin_account(
    data: AdminRegisterRequest
):

    # Verify secret key
    if data.admin_setup_key != ADMIN_SETUP_KEY:

        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "message": "Invalid admin setup key",
                "error_code": "INVALID_ADMIN_SETUP_KEY"
            }
        )


    admin, error = await register_admin(
        data
    )


    if error == "EMAIL_EXISTS":

        raise HTTPException(
            status_code=409,
            detail={
                "success": False,
                "message": "Email already registered",
                "error_code": "EMAIL_ALREADY_EXISTS"
            }
        )


    if error == "USERNAME_EXISTS":

        raise HTTPException(
            status_code=409,
            detail={
                "success": False,
                "message": "Username already exists",
                "error_code": "USERNAME_ALREADY_EXISTS"
            }
        )


    return {

        "success": True,

        "message": "Admin registered successfully",

        "data": {

            "id": str(
                admin["_id"]
            ),

            "username": admin["username"],

            "email": admin["email"],

            "full_name": admin["full_name"],

            "phone": admin["phone"],

            "department": admin["department"],

            "role": "admin",

            "is_active": True
        }
    }


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login"
)
async def login(
    data: LoginRequest
):

    token, error = await authenticate_user(

        data.email,

        data.password
    )


    if error == "ACCOUNT_INACTIVE":

        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "message": "Account is deactivated",
                "error_code": "ACCOUNT_INACTIVE"
            }
        )


    if error == "INVALID_CREDENTIALS":

        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "message": "Invalid email or password",
                "error_code": "INVALID_CREDENTIALS"
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