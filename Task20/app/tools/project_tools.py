from app.services.project_service import (
    create_project,
    get_project,
    add_project_member
)


def create_project_tool(
    name: str,
    description: str = ""
) -> dict:

    return create_project(
        name=name,
        description=description
    )


def get_project_tool(
    project_id: int
) -> dict:

    return get_project(
        project_id=project_id
    )


def add_project_member_tool(
    project_id: int,
    employee_id: int
) -> dict:

    return add_project_member(
        project_id=project_id,
        employee_id=employee_id
    )