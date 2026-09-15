from pydantic import BaseModel
from typing import Optional


class ProjectTaskCreate(BaseModel):
    project_id: str
    title: str
    priority: str = "medium"
    assigned_to: Optional[str] = None


class UpdateTaskStatus(BaseModel):
    task_id: str
    status: str