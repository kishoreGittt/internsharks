from typing import List

from pydantic import BaseModel


class Project(BaseModel):
    project_id: int
    name: str
    description: str = ""
    members: List[int] = []
    status: str = "active"