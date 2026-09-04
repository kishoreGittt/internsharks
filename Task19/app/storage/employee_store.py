from app.models.employee import Employee


employees = [
    Employee(
        employee_id=101,
        name="Arun",
        email="arun@example.com",
        department="IT",
        designation="Software Developer",
        casual_leave=8,
        sick_leave=5
    ),

    Employee(
        employee_id=102,
        name="Priya",
        email="priya@example.com",
        department="HR",
        designation="HR Executive",
        casual_leave=6,
        sick_leave=4
    ),

    Employee(
        employee_id=103,
        name="Rahul",
        email="rahul@example.com",
        department="Finance",
        designation="Accountant",
        casual_leave=10,
        sick_leave=7
    )
]