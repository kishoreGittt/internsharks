from datetime import date

from app.models.leave import LeaveRequest
from app.storage.employee_store import employees
from app.storage.leave_store import (
    leave_requests
)


def find_employee(employee_id: int):

    for employee in employees:

        if employee.employee_id == employee_id:
            return employee

    return None


def get_employee(employee_id: int):

    employee = find_employee(employee_id)

    if not employee:

        raise ValueError(
            f"Employee {employee_id} not found."
        )

    return employee.model_dump()


def get_leave_balance(employee_id: int):

    employee = find_employee(employee_id)

    if not employee:

        raise ValueError(
            f"Employee {employee_id} not found."
        )

    return {
        "employee_id": employee.employee_id,
        "name": employee.name,
        "casual_leave": employee.casual_leave,
        "sick_leave": employee.sick_leave
    }


def calculate_leave_days(
    start_date: date,
    end_date: date
):

    if end_date < start_date:

        raise ValueError(
            "End date cannot be before start date."
        )

    return (
        end_date - start_date
    ).days + 1


def apply_leave(
    employee_id: int,
    leave_type: str,
    start_date: str,
    end_date: str,
    reason: str
):

    employee = find_employee(employee_id)

    if not employee:

        raise ValueError(
            f"Employee {employee_id} not found."
        )

    if leave_type not in ["casual", "sick"]:

        raise ValueError(
            "Leave type must be casual or sick."
        )

    if not reason or not reason.strip():

        raise ValueError(
            "Leave reason is required."
        )

    try:

        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)

    except ValueError:

        raise ValueError(
            "Dates must use YYYY-MM-DD format."
        )

    total_days = calculate_leave_days(
        start,
        end
    )

    if leave_type == "casual":

        available_balance = employee.casual_leave

    else:

        available_balance = employee.sick_leave

    if total_days > available_balance:

        raise ValueError(
            f"Insufficient {leave_type} leave balance. "
            f"Available: {available_balance}, "
            f"Requested: {total_days}."
        )

    from app.storage.leave_store import (
        next_leave_request_id
    )

    request_id = (
        f"LR-{next_leave_request_id:04d}"
    )

    import app.storage.leave_store as store

    store.next_leave_request_id += 1

    request = LeaveRequest(
        leave_request_id=request_id,
        employee_id=employee_id,
        leave_type=leave_type,
        start_date=start,
        end_date=end,
        reason=reason,
        status="pending"
    )

    leave_requests.append(request)

    return {
        "success": True,
        "leave_request_id": request_id,
        "employee_id": employee_id,
        "leave_type": leave_type,
        "start_date": start_date,
        "end_date": end_date,
        "days": total_days,
        "reason": reason,
        "status": "pending"
    }


def get_leave_requests(employee_id: int):

    employee = find_employee(employee_id)

    if not employee:

        raise ValueError(
            f"Employee {employee_id} not found."
        )

    requests = []

    for request in leave_requests:

        if request.employee_id == employee_id:

            requests.append(
                request.model_dump(mode="json")
            )

    return {
        "employee_id": employee_id,
        "requests": requests
    }