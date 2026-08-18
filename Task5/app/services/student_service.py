from app.database.mongodb import student_collection


# ============================================================
# CREATE STUDENT
# ============================================================

async def create_student(student_data: dict):

    result = await student_collection.insert_one(
        student_data
    )

    # Fetch the created document without MongoDB ObjectId
    created_student = await student_collection.find_one(
        {
            "_id": result.inserted_id
        },
        {
            "_id": 0
        }
    )

    return created_student


# ============================================================
# CHECK STUDENT EXISTS
# ============================================================

async def student_exists(student_id: int):

    student = await student_collection.find_one(
        {
            "id": student_id
        }
    )

    return student is not None


# ============================================================
# GET ALL STUDENTS
# ============================================================

async def get_all_students():

    students = await student_collection.find(
        {},
        {
            "_id": 0
        }
    ).to_list(length=None)

    return students


# ============================================================
# GET STUDENT BY ID
# ============================================================

async def get_student_by_id(student_id: int):

    student = await student_collection.find_one(
        {
            "id": student_id
        },
        {
            "_id": 0
        }
    )

    return student


# ============================================================
# UPDATE STUDENT
# ============================================================

async def update_student(
    student_id: int,
    student_data: dict
):

    result = await student_collection.update_one(
        {
            "id": student_id
        },
        {
            "$set": student_data
        }
    )

    if result.matched_count == 0:
        return None

    updated_student = await student_collection.find_one(
        {
            "id": student_id
        },
        {
            "_id": 0
        }
    )

    return updated_student


# ============================================================
# DELETE STUDENT
# ============================================================

async def delete_student(student_id: int):

    student = await student_collection.find_one(
        {
            "id": student_id
        },
        {
            "_id": 0
        }
    )

    if student is None:
        return None

    await student_collection.delete_one(
        {
            "id": student_id
        }
    )

    return student


# ============================================================
# DELETE ALL STUDENTS
# ============================================================

async def delete_all_students():

    result = await student_collection.delete_many({})

    return result.deleted_count


# ============================================================
# SEARCH STUDENTS
# ============================================================

async def search_students(
    name: str | None = None,
    course: str | None = None
):

    query = {}

    # Search by name
    if name is not None:

        query["name"] = {
            "$regex": name.strip(),
            "$options": "i"
        }

    # Search/filter by course
    if course is not None:

        query["course"] = {
            "$regex": course.strip(),
            "$options": "i"
        }

    students = await student_collection.find(
        query,
        {
            "_id": 0
        }
    ).to_list(length=None)

    return students