from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    full_name: str
    phone: str
    role: str
    is_active: bool