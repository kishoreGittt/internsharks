from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobRecord(BaseModel):
    job_id: str
    file_name: str
    file_path: str
    analysis_type: str

    status: JobStatus = JobStatus.QUEUED

    result: dict[str, Any] | None = None
    error: str | None = None
    processed_by: str | None = None

    created_at: datetime = Field(default_factory=utc_now)
    started_at: datetime | None = None
    completed_at: datetime | None = None


class JobSubmitResponse(BaseModel):
    success: bool = True
    status_code: int = 202
    data: dict[str, Any]


class JobResponse(BaseModel):
    success: bool = True
    status_code: int = 200
    data: dict[str, Any]


class JobListResponse(BaseModel):
    success: bool = True
    status_code: int = 200
    data: dict[str, Any]


class QueueResponse(BaseModel):
    success: bool = True
    status_code: int = 200
    data: dict[str, Any]