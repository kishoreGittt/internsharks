from typing import Dict, List

from app.models.project import Project
from app.models.task import ProjectTask


projects: Dict[int, Project] = {}

tasks: Dict[int, ProjectTask] = {}


next_project_id = 1
next_task_id = 1


def generate_project_id() -> int:
    global next_project_id

    project_id = next_project_id
    next_project_id += 1

    return project_id


def generate_task_id() -> int:
    global next_task_id

    task_id = next_task_id
    next_task_id += 1

    return task_id


def get_all_projects() -> List[Project]:
    return list(projects.values())


def get_all_tasks() -> List[ProjectTask]:
    return list(tasks.values())