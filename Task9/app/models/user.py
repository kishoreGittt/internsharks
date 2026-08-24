from typing import Optional, Literal

from pydantic import BaseModel, Field


# ============================================================
# USER PROFILE UPDATE
# ============================================================

class UserUpdate(BaseModel):

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
        min_length=10,
        max_length=15
    )

    department: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100
    )


# ============================================================
# ROLE UPDATE
# ============================================================

class RoleUpdate(BaseModel):

    role: Literal[
        "user",
        "admin"
    ]


# ============================================================
# STATUS UPDATE
# ============================================================

class StatusUpdate(BaseModel):

    is_active: bool