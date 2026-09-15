from app.database.mongodb import employees_collection


async def find_employee(name: str):
    employee = await employees_collection.find_one(
        {
            "name": {
                "$regex": name,
                "$options": "i"
            }
        },
        {"_id": 0}
    )

    if not employee:
        return {
            "found": False,
            "message": "Employee not found"
        }

    return {
        "found": True,
        "employee": employee
    }