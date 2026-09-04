from app.services.employee_service import (
    apply_leave,
    get_leave_requests
)


def tool_apply_leave(
    employee_id: int,
    leave_type: str,
    start_date: str,
    end_date: str,
    reason: str
):

    return apply_leave(
        employee_id,
        leave_type,
        start_date,
        end_date,
        reason
    )


def tool_get_leave_requests(
    employee_id: int
):

    return get_leave_requests(
        employee_id
    )