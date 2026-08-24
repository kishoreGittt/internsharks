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
        min_length=6
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


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponseData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshResponseData(BaseModel):
    access_token: str
    token_type: str


class MessageResponse(BaseModel):
    success: bool
    message: str
    data: dict | None = None