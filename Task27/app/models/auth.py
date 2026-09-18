from pydantic import (
    BaseModel,
    EmailStr,
    Field
)


class RegisterRequest(BaseModel):

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=100
    )


class LoginRequest(BaseModel):

    email: EmailStr

    password: str


class TokenResponse(BaseModel):

    success: bool

    status_code: int

    access_token: str

    token_type: str


class UserResponse(BaseModel):

    success: bool = True

    status_code: int = 200

    user_id: str

    email: EmailStr