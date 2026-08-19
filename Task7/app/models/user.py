from pydantic import BaseModel, EmailStr, Field


# ============================================================
# Register User
# ============================================================

class UserCreate(BaseModel):

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


# ============================================================
# Login User
# ============================================================

class UserLogin(BaseModel):

    email: EmailStr

    password: str = Field(
        ...,
        min_length=6,
        max_length=100
    )


# ============================================================
# User Response
# Password is intentionally NOT included
# ============================================================

class UserResponse(BaseModel):

    id: str
    username: str
    email: EmailStr