from typing import Optional

from app.models.project import Project
from app.models.task import ProjectTask

from app.storage.project_store import (
    projects,
    tasks,
    generate_project_id,
    generate_task_id
)

from app.services.employee_service import find_employee


ALLOWED_PROJECT_STATUS = {
    "active",
    "completed"
}

ALLOWED_PRIORITY = {
    "low",
    "medium",
    "high"
}

ALLOWED_TASK_STATUS = {
    "todo",
    "in_progress",
    "completed"
}


def create_project(
    name: str,
    description: str = ""
) -> dict:

    name = name.strip()

    if not name:
        raise ValueError("Project name cannot be empty.")

    for project in projects.values():
        if project.name.lower() == name.lower():
            raise ValueError(
                f"Project '{name}' already exists."
            )

    project_id = generate_project_id()

    project = Project(
        project_id=project_id,
        name=name,
        description=description,
        members=[],
        status="active"
    )

    projects[project_id] = project

    return {
        "project_id": project.project_id,
        "name": project.name,
        "description": project.description,
        "members": project.members,
        "status": project.status
    }


def get_project(project_id: int) -> dict:

    project = projects.get(project_id)

    if not project:
        raise ValueError(
            f"Project {project_id} not found."
        )

    return project.model_dump()


def add_project_member(
    project_id: int,
    employee_id: int
) -> dict:

    project = projects.get(project_id)

    if not project:
        raise ValueError(
            f"Project {project_id} not found."
        )

    employee = find_employee(
        employee_id=employee_id
    )

    if not employee:
        raise ValueError(
            f"Employee {employee_id} does not exist."
        )

    if employee_id in project.members:
        raise ValueError(
            f"Employee {employee_id} is already a member."
        )

    project.members.append(employee_id)

    return {
        "project_id": project_id,
        "employee_id": employee_id,
        "employee_name": employee["name"],
        "message": (
            f"{employee['name']} added to project "
            f"{project.name}."
        )
    }


def create_project_task(
    project_id: int,
    title: str,
    priority: str,
    assigned_to: Optional[int] = None
) -> dict:

    project = projects.get(project_id)

    if not project:
        raise ValueError(
            f"Project {project_id} not found."
        )

    title = title.strip()

    if not title:
        raise ValueError(
            "Task title cannot be empty."
        )

    priority = priority.lower()

    if priority not in ALLOWED_PRIORITY:
        raise ValueError(
            "Invalid priority. "
            "Allowed values: low, medium, high."
        )

    if assigned_to is not None:

        employee = find_employee(
            employee_id=assigned_to
        )

        if not employee:
            raise ValueError(
                f"Employee {assigned_to} does not exist."
            )

        if assigned_to not in project.members:
            raise ValueError(
                f"Employee {assigned_to} is not a "
                f"member of project {project_id}."
            )

    task_id = generate_task_id()

    task = ProjectTask(
        task_id=task_id,
        project_id=project_id,
        title=title,
        priority=priority,
        status="todo",
        assigned_to=assigned_to
    )

    tasks[task_id] = task

    return {
        "task_id": task.task_id,
        "project_id": task.project_id,
        "title": task.title,
        "priority": task.priority,
        "status": task.status,
        "assigned_to": task.assigned_to
    }


def list_project_tasks(
    project_id: int
) -> dict:

    project = projects.get(project_id)

    if not project:
        raise ValueError(
            f"Project {project_id} not found."
        )

    project_tasks = [
        task.model_dump()
        for task in tasks.values()
        if task.project_id == project_id
    ]

    return {
        "project_id": project_id,
        "tasks": project_tasks
    }


def update_task_status(
    task_id: int,
    status: str
) -> dict:

    task = tasks.get(task_id)

    if not task:
        raise ValueError(
            f"Task {task_id} not found."
        )

    status = status.lower()

    if status not in ALLOWED_TASK_STATUS:
        raise ValueError(
            "Invalid status. "
            "Allowed values: "
            "todo, in_progress, completed."
        )

    task.status = status

    return {
        "task_id": task.task_id,
        "status": task.status,
        "message": f"Task {task_id} status updated."
    }