from datetime import datetime

from pydantic import BaseModel, Field, field_validator


ALLOWED_STATUSES = {
    "todo",
    "in_progress",
    "completed",
}

ALLOWED_PRIORITIES = {
    "low",
    "medium",
    "high",
}


class TaskCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=200
    )

    description: str = Field(
        ...,
        min_length=1,
        max_length=2000
    )

    status: str = "todo"

    priority: str = "medium"

    assigned_to: str | None = None

    due_date: datetime | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        if value not in ALLOWED_STATUSES:
            raise ValueError(
                "Invalid task status"
            )

        return value

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value):
        if value not in ALLOWED_PRIORITIES:
            raise ValueError(
                "Invalid task priority"
            )

        return value


class TaskUpdate(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=200
    )

    description: str = Field(
        ...,
        min_length=1,
        max_length=2000
    )

    status: str

    priority: str

    assigned_to: str | None = None

    due_date: datetime | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        if value not in ALLOWED_STATUSES:
            raise ValueError("Invalid task status")

        return value

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value):
        if value not in ALLOWED_PRIORITIES:
            raise ValueError("Invalid task priority")

        return value


class TaskStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        if value not in ALLOWED_STATUSES:
            raise ValueError("Invalid task status")

        return value


class TaskAssign(BaseModel):
    user_id: str


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    status: str
    priority: str
    created_by: str
    assigned_to: str | None
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime