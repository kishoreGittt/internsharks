from app.tools.employee_tools import find_employee

from app.tools.project_tools import (
    list_projects,
    get_project,
    create_project,
    add_project_member
)

from app.tools.task_tools import (
    get_project_tasks,
    get_task,
    create_project_task,
    update_task_status,
    delete_project_task
)


TOOL_REGISTRY = {

    "find_employee": {
        "function": find_employee,
        "requires_approval": False
    },

    "list_projects": {
        "function": list_projects,
        "requires_approval": False
    },

    "get_project": {
        "function": get_project,
        "requires_approval": False
    },

    "get_project_tasks": {
        "function": get_project_tasks,
        "requires_approval": False
    },

    "get_task": {
        "function": get_task,
        "requires_approval": False
    },

    "create_project": {
        "function": create_project,
        "requires_approval": True
    },

    "add_project_member": {
        "function": add_project_member,
        "requires_approval": True
    },

    "create_project_task": {
        "function": create_project_task,
        "requires_approval": True
    },

    "update_task_status": {
        "function": update_task_status,
        "requires_approval": True
    },

    "delete_project_task": {
        "function": delete_project_task,
        "requires_approval": True
    }
}


def get_tool(name: str):

    return TOOL_REGISTRY.get(name)