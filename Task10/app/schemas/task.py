from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=200
    )

    description: str | None = Field(
        default=None,
        max_length=2000
    )

    status: TaskStatus = TaskStatus.TODO

    priority: TaskPriority = TaskPriority.MEDIUM

    assigned_to: str | None = None

    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=200
    )

    description: str | None = Field(
        default=None,
        max_length=2000
    )

    status: TaskStatus

    priority: TaskPriority

    assigned_to: str | None = None

    due_date: datetime | None = None


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskAssignRequest(BaseModel):
    user_id: str = Field(
        ...,
        min_length=1
    )


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    created_by: str
    assigned_to: str | None
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    success: bool
    page: int
    limit: int
    total: int
    data: list[TaskResponse]