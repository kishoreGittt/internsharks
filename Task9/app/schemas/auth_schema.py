from pydantic import BaseModel, EmailStr, Field


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

    full_name: str | None = None

    phone: str | None = None


class LoginRequest(BaseModel):

    email: EmailStr

    password: str


class TokenResponse(BaseModel):

    access_token: str
    refresh_token: str
    token_type: str


class RefreshResponse(BaseModel):

    access_token: str
    token_type: str


class MessageResponse(BaseModel):

    success: bool
    message: str
    data: dict | None = None