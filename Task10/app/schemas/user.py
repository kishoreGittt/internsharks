from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    full_name: str | None
    role: str
    is_active: bool
    created_at: datetime


class UserListResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    full_name: str | None
    role: str
    is_active: bool
    created_at: datetime