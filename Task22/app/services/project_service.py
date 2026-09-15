from datetime import datetime, timezone
from bson import ObjectId
from app.storage.database import projects_collection, employees_collection, tasks_collection
from app.reliability.errors import NonRetryableError

def create_project(name):
    if not name:
        raise NonRetryableError("Project name is required", "PROJECT_NAME_REQUIRED")
    doc = {"name": name, "created_at": datetime.now(timezone.utc)}
    result = projects_collection.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return doc

def add_employee(name):
    if not name:
        raise NonRetryableError("Employee name is required", "EMPLOYEE_NAME_REQUIRED")
    doc = {"name": name, "created_at": datetime.now(timezone.utc)}
    result = employees_collection.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return doc

def create_task(project_id, employee_id, title, priority="medium"):
    if priority not in {"low", "medium", "high"}:
        raise NonRetryableError("Invalid priority", "INVALID_PRIORITY")
    if not title:
        raise NonRetryableError("Task title is required", "TASK_TITLE_REQUIRED")
    doc = {
        "project_id": project_id,
        "employee_id": employee_id,
        "title": title,
        "priority": priority,
        "created_at": datetime.now(timezone.utc)
    }
    result = tasks_collection.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return doc
