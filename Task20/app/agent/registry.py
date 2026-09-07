from typing import Any, Callable, Dict


from app.tools.employee_tools import (
    find_employee_tool
)

from app.tools.project_tools import (
    create_project_tool,
    get_project_tool,
    add_project_member_tool
)

from app.tools.task_tools import (
    create_project_task_tool,
    list_project_tasks_tool,
    update_task_status_tool
)


TOOL_FUNCTIONS: Dict[str, Callable] = {
    "find_employee": find_employee_tool,
    "create_project": create_project_tool,
    "get_project": get_project_tool,
    "add_project_member": add_project_member_tool,
    "create_project_task": create_project_task_tool,
    "list_project_tasks": list_project_tasks_tool,
    "update_task_status": update_task_status_tool,
}


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "find_employee",
            "description": (
                "Find an employee by name or employee ID. "
                "Use this before adding or assigning an employee."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Employee name"
                    },
                    "employee_id": {
                        "type": "integer",
                        "description": "Employee ID"
                    }
                }
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "create_project",
            "description": "Create a new project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Project name"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description"
                    }
                },
                "required": ["name"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_project",
            "description": "Retrieve a project by project ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "integer",
                        "description": "Project ID"
                    }
                },
                "required": ["project_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "add_project_member",
            "description": (
                "Add an existing employee to an existing project."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "integer"
                    },
                    "employee_id": {
                        "type": "integer"
                    }
                },
                "required": [
                    "project_id",
                    "employee_id"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "create_project_task",
            "description": (
                "Create a task inside a project. "
                "The assigned employee must exist and "
                "must be a project member."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "integer"
                    },
                    "title": {
                        "type": "string"
                    },
                    "priority": {
                        "type": "string",
                        "enum": [
                            "low",
                            "medium",
                            "high"
                        ]
                    },
                    "assigned_to": {
                        "type": "integer"
                    }
                },
                "required": [
                    "project_id",
                    "title",
                    "priority"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "list_project_tasks",
            "description": (
                "List all tasks belonging to a project."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "integer"
                    }
                },
                "required": ["project_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "update_task_status",
            "description": (
                "Update a project task status."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer"
                    },
                    "status": {
                        "type": "string",
                        "enum": [
                            "todo",
                            "in_progress",
                            "completed"
                        ]
                    }
                },
                "required": [
                    "task_id",
                    "status"
                ]
            }
        }
    }
]


def get_tool_function(
    tool_name: str
) -> Callable:

    function = TOOL_FUNCTIONS.get(tool_name)

    if not function:
        raise ValueError(
            f"Unknown tool: {tool_name}"
        )

    return function