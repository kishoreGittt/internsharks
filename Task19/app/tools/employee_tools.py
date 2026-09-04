from app.services.employee_service import (
    get_employee,
    get_leave_balance
)


def tool_get_employee(employee_id: int):

    return get_employee(employee_id)


def tool_get_leave_balance(employee_id: int):

    return get_leave_balance(employee_id)