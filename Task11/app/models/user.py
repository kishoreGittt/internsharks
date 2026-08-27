from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=8,
        max_length=128
    )

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    phone: str | None = Field(
        default=None,
        max_length=20
    )

    department: str | None = Field(
        default=None,
        max_length=100
    )

    # ADD THIS
    role: str = Field(
        default="user",
        pattern="^(user|admin)$"
    )


class UserLogin(BaseModel):
    email: EmailStr

    password: str = Field(
        ...,
        min_length=1
    )


class UserUpdate(BaseModel):
    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=50
    )

    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    phone: str | None = Field(
        default=None,
        max_length=20
    )

    department: str | None = Field(
        default=None,
        max_length=100
    )


class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    full_name: str
    phone: str | None = None
    department: str | None = None
    role: str
    is_active: bool


class TokenResponse(BaseModel):
    success: bool
    message: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"