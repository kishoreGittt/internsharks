from typing import Dict, List, Optional


employees: List[Dict] = [
    {
        "employee_id": 101,
        "name": "Arun",
        "designation": "Backend Developer"
    },
    {
        "employee_id": 102,
        "name": "Priya",
        "designation": "UI/UX Designer"
    },
    {
        "employee_id": 103,
        "name": "Rahul",
        "designation": "QA Engineer"
    }
]


def find_employee(
    name: Optional[str] = None,
    employee_id: Optional[int] = None
):
    if employee_id is not None:
        for employee in employees:
            if employee["employee_id"] == employee_id:
                return employee

    if name:
        name_lower = name.strip().lower()

        for employee in employees:
            if employee["name"].lower() == name_lower:
                return employee

    return None