from app.tools.calculator import calculator
from app.tools.date_tool import get_current_date
from app.tools.task_tool import get_task


TOOL_REGISTRY = {
    "calculator": calculator,
    "get_current_date": get_current_date,
    "get_task": get_task
}


def get_registered_tool(tool_name: str):
    return TOOL_REGISTRY.get(tool_name)


def is_registered_tool(tool_name: str) -> bool:
    return tool_name in TOOL_REGISTRY