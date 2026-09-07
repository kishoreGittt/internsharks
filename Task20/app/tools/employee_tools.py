from typing import Optional

from app.services.employee_service import find_employee


def find_employee_tool(
    name: Optional[str] = None,
    employee_id: Optional[int] = None
) -> dict:

    if name is None and employee_id is None:
        raise ValueError(
            "Either name or employee_id is required."
        )

    employee = find_employee(
        name=name,
        employee_id=employee_id
    )

    if not employee:
        return {
            "success": False,
            "found": False,
            "message": "Employee not found."
        }

    return {
        "success": True,
        "found": True,
        "employee": employee
    }