from typing import Optional


EMPLOYEES = [
    {
        "id": 1,
        "name": "Kishore",
        "department": "AI/ML",
        "role": "AI/ML Engineer",
        "email": "kishore@example.com",
    },
    {
        "id": 2,
        "name": "Arun",
        "department": "Backend",
        "role": "Python Developer",
        "email": "arun@example.com",
    },
    {
        "id": 3,
        "name": "Priya",
        "department": "HR",
        "role": "HR Manager",
        "email": "priya@example.com",
    },
]


def find_employee(name: str) -> Optional[dict]:
    """Find an employee by name."""

    name = name.strip().lower()

    for employee in EMPLOYEES:
        if employee["name"].lower() == name:
            return employee

    return None


def get_all_employees() -> list:
    """Return all employees."""

    return EMPLOYEES


def find_employee_by_id(employee_id: int) -> Optional[dict]:
    """Find employee by ID."""

    for employee in EMPLOYEES:
        if employee["id"] == employee_id:
            return employee

    return None