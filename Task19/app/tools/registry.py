from app.tools.employee_tools import (
    tool_get_employee,
    tool_get_leave_balance
)

from app.tools.leave_tools import (
    tool_apply_leave,
    tool_get_leave_requests
)

from app.tools.holiday_tools import (
    tool_get_company_holidays
)


TOOL_REGISTRY = {

    "get_employee":
        tool_get_employee,

    "get_leave_balance":
        tool_get_leave_balance,

    "get_company_holidays":
        tool_get_company_holidays,

    "apply_leave":
        tool_apply_leave,

    "get_leave_requests":
        tool_get_leave_requests
}


def execute_tool(
    tool_name: str,
    arguments: dict
):

    if tool_name not in TOOL_REGISTRY:

        raise ValueError(
            f"Unknown tool: {tool_name}"
        )

    tool_function = TOOL_REGISTRY[
        tool_name
    ]

    return tool_function(
        **arguments
    )