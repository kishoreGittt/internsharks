from typing import Optional

from pydantic import BaseModel


class ProjectTask(BaseModel):
    task_id: int
    project_id: int
    title: str
    priority: str
    status: str = "todo"
    assigned_to: Optional[int] = None