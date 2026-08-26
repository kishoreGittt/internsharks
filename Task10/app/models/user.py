# from pydantic import BaseModel, EmailStr, Field, ConfigDict


# class UserRegister(BaseModel):

#     username: str = Field(
#         ...,
#         min_length=3,
#         max_length=50
#     )

#     email: EmailStr

#     password: str = Field(
#         ...,
#         min_length=8,
#         max_length=100
#     )


# class UserLogin(BaseModel):

#     email: EmailStr

#     password: str = Field(
#         ...,
#         min_length=1,
#         max_length=100
#     )


# class UserResponse(BaseModel):

#     id: str
#     username: str
#     email: EmailStr
#     role: str
#     is_active: bool

#     model_config = ConfigDict(
#         from_attributes=True
#     )


# # from typing import Literal

# # from pydantic import BaseModel, EmailStr, Field, ConfigDict


# # # ============================================================
# # # USER REGISTRATION
# # # ============================================================

# # class UserRegister(BaseModel):

# #     username: str = Field(
# #         ...,
# #         min_length=3,
# #         max_length=50
# #     )

# #     email: EmailStr

# #     password: str = Field(
# #         ...,
# #         min_length=8,
# #         max_length=100
# #     )

# #     role: Literal["user", "admin"] = "user"


# # # ============================================================
# # # USER LOGIN
# # # ============================================================

# # class UserLogin(BaseModel):

# #     email: EmailStr

# #     password: str = Field(
# #         ...,
# #         min_length=1,
# #         max_length=100
# #     )


# # # ============================================================
# # # USER RESPONSE
# # # ============================================================

# # class UserResponse(BaseModel):

# #     id: str

# #     username: str

# #     email: EmailStr

# #     role: Literal["user", "admin"]

# #     is_active: bool

# #     model_config = ConfigDict(
# #         from_attributes=True
# #     )














from typing import Literal

from pydantic import BaseModel, EmailStr, Field, ConfigDict


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
        max_length=100
    )

    role: Literal["user", "admin"] = "user"


class UserLogin(BaseModel):

    email: EmailStr

    password: str = Field(
        ...,
        min_length=1,
        max_length=100
    )


class UserResponse(BaseModel):

    id: str
    username: str
    email: EmailStr
    role: Literal["user", "admin"]
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )