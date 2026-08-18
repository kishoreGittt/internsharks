from pydantic import BaseModel, EmailStr


# ============================================================
# Student Model
# ============================================================

class Student(BaseModel):

    id: int
    name: str
    email: EmailStr
    course: str