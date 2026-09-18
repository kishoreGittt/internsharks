from app.tools.project_tools import (
    tool_get_project,
    tool_get_project_members,
    tool_get_project_tasks,
    tool_create_project_task,
    tool_update_project_task_status
)


TOOLS = [

    {
        "type": "function",
        "function": {
            "name": "get_project",
            "description": (
                "Get a project using project ID or project name."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID."
                    },
                    "project_name": {
                        "type": "string",
                        "description": "Project name."
                    }
                },
                "additionalProperties": False
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_project_members",
            "description": "Get members of a project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID."
                    }
                },
                "required": [
                    "project_id"
                ],
                "additionalProperties": False
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_project_tasks",
            "description": "Get current tasks for a project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID."
                    }
                },
                "required": [
                    "project_id"
                ],
                "additionalProperties": False
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "create_project_task",
            "description": "Create a new task in a project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID."
                    },
                    "title": {
                        "type": "string",
                        "description": "Task title."
                    },
                    "description": {
                        "type": "string",
                        "description": "Task description."
                    },
                    "assigned_to": {
                        "type": "string",
                        "description": "Optional user ID."
                    }
                },
                "required": [
                    "project_id",
                    "title"
                ],
                "additionalProperties": False
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "update_project_task_status",
            "description": (
                "Update the status of an existing project task."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID."
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Task ID."
                    },
                    "status": {
                        "type": "string",
                        "enum": [
                            "todo",
                            "in_progress",
                            "done",
                            "blocked"
                        ],
                        "description": "New task status."
                    }
                },
                "required": [
                    "project_id",
                    "task_id",
                    "status"
                ],
                "additionalProperties": False
            }
        }
    }
]


TOOL_FUNCTIONS = {

    "get_project":
        tool_get_project,

    "get_project_members":
        tool_get_project_members,

    "get_project_tasks":
        tool_get_project_tasks,

    "create_project_task":
        tool_create_project_task,

    "update_project_task_status":
        tool_update_project_task_status
}