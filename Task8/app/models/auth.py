from pydantic import (
    BaseModel,
    EmailStr,
    Field
)


# ============================================================
# NORMAL USER REGISTRATION
# ============================================================

class RegisterRequest(BaseModel):

    username: str = Field(
        ...,
        min_length=3,
        max_length=50
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=6,
        max_length=100
    )

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    phone: str = Field(
        ...,
        min_length=10,
        max_length=15
    )

    department: str = Field(
        ...,
        min_length=2,
        max_length=100
    )


# ============================================================
# ADMIN REGISTRATION
# ============================================================

class AdminRegisterRequest(BaseModel):

    username: str = Field(
        ...,
        min_length=3,
        max_length=50
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=6,
        max_length=100
    )

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    phone: str = Field(
        ...,
        min_length=10,
        max_length=15
    )

    department: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    admin_setup_key: str


# ============================================================
# LOGIN
# ============================================================

class LoginRequest(BaseModel):

    email: EmailStr

    password: str