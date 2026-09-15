from bson import ObjectId

from app.database.mongodb import (
    projects_collection,
    employees_collection
)


async def list_projects():
    projects = []

    cursor = projects_collection.find(
        {},
        {"_id": 0}
    )

    async for project in cursor:
        projects.append(project)

    return projects


async def get_project(project_id: str):

    project = await projects_collection.find_one(
        {"project_id": project_id},
        {"_id": 0}
    )

    if not project:
        return {
            "found": False,
            "message": "Project not found"
        }

    return {
        "found": True,
        "project": project
    }


async def create_project(
    name: str,
    description: str = ""
):

    existing = await projects_collection.find_one(
        {"name": name}
    )

    if existing:
        raise ValueError(
            "Project with this name already exists"
        )

    project_id = str(ObjectId())

    project = {
        "project_id": project_id,
        "name": name,
        "description": description,
        "members": []
    }

    await projects_collection.insert_one(project)

    return {
        "success": True,
        "project": project
    }


async def add_project_member(
    project_id: str,
    employee_id: str
):

    project = await projects_collection.find_one(
        {"project_id": project_id}
    )

    if not project:
        raise ValueError("Project not found")

    employee = await employees_collection.find_one(
        {"employee_id": employee_id}
    )

    if not employee:
        raise ValueError("Employee not found")

    if employee_id in project.get("members", []):
        return {
            "success": True,
            "message": "Employee already belongs to project"
        }

    await projects_collection.update_one(
        {"project_id": project_id},
        {
            "$push": {
                "members": employee_id
            }
        }
    )

    return {
        "success": True,
        "message": "Employee added to project"
    }