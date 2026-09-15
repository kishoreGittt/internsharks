from typing import Optional

from pydantic import BaseModel


class CreateProjectInput(BaseModel):
    name: str


class AddProjectMemberInput(BaseModel):
    project_id: int
    employee_id: int


class CreateProjectTaskInput(BaseModel):
    project_id: int
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    assigned_to: Optional[int] = None


class UpdateTaskStatusInput(BaseModel):
    task_id: int
    status: str


class DeleteProjectTaskInput(BaseModel):
    task_id: int