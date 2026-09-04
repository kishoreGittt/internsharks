from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class ApplyLeaveRequest(BaseModel):
    employee_id: int
    leave_type: Literal["casual", "sick"]
    start_date: date
    end_date: date
    reason: str = Field(min_length=3)


class LeaveRequest(BaseModel):
    leave_request_id: str
    employee_id: int
    leave_type: str
    start_date: date
    end_date: date
    reason: str
    status: str