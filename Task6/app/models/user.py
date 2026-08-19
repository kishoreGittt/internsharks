from pydantic import BaseModel, EmailStr, Field


# ============================================================
# Register User Request
# ============================================================

class UserRegister(BaseModel):

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username of the user"
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="User password"
    )


# ============================================================
# Login Request
# ============================================================

class UserLogin(BaseModel):

    email: EmailStr

    password: str = Field(
        ...,
        min_length=1,
        max_length=100
    )


# ============================================================
# User Response
# ============================================================

class UserResponse(BaseModel):

    id: str
    username: str
    email: EmailStr


# ============================================================
# Standard API Response
# ============================================================

class APIResponse(BaseModel):

    success: bool

    error_code: str | None

    message: str

    data: dict | None