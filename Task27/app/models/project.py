from pydantic import (
    BaseModel,
    Field
)


class ProjectTask(BaseModel):

    task_id: str

    title: str

    description: str

    status: str


class ProjectMember(BaseModel):

    user_id: str

    name: str

    role: str


class ProjectResponse(BaseModel):

    project_id: str

    name: str

    description: str

    manager: dict

    members: list[ProjectMember]

    tasks: list[ProjectTask]