from typing import Optional, Literal

from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    username: str
    email: str
    full_name: str
    phone: str
    department: str
    role: Literal["user", "admin"]
    is_active: bool


class ProfileUpdateRequest(BaseModel):
    username: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=50
    )

    full_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    phone: Optional[str] = Field(
        default=None,
        min_length=7,
        max_length=20
    )

    department: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100
    )


class RoleUpdateRequest(BaseModel):
    role: Literal["user", "admin"]


class StatusUpdateRequest(BaseModel):
    is_active: bool