from fastapi import APIRouter, HTTPException, Query

from app.models.student import Student

from app.services.student_service import (
    create_student,
    get_all_students,
    get_student_by_id,
    student_exists,
    update_student,
    delete_student,
    search_students
)


# ============================================================
# Router
# ============================================================

router = APIRouter()


# ============================================================
# CREATE STUDENT
# ============================================================

@router.post("/students/create", status_code=201)
async def create_student_endpoint(student: Student):

    # --------------------------------------------------------
    # Check duplicate ID
    # --------------------------------------------------------

    if await student_exists(student.id):

        raise HTTPException(
            status_code=409,
            detail={
                "status": "error",
                "message": (
                    f"Student with ID {student.id} "
                    "already exists"
                ),
                "error": "Duplicate student ID"
            }
        )

    # --------------------------------------------------------
    # Convert Pydantic model to dictionary
    # --------------------------------------------------------

    student_data = student.model_dump()

    # --------------------------------------------------------
    # Store in MongoDB
    # --------------------------------------------------------

    created_student = await create_student(
        student_data
    )

    return {
        "status": "success",
        "message": "Student added successfully",
        "data": created_student
    }


# ============================================================
# GET ALL STUDENTS
# ============================================================

@router.get("/students/all")
async def get_all_students_endpoint():

    students = await get_all_students()

    if not students:

        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": "No students are currently available",
                "error": "No student records found"
            }
        )

    return {
        "status": "success",
        "message": "Students retrieved successfully",
        "count": len(students),
        "data": students
    }


# ============================================================
# SEARCH STUDENTS
# ============================================================

@router.get("/students/search")
async def search_students_endpoint(
    name: str | None = Query(default=None),
    course: str | None = Query(default=None)
):

    # --------------------------------------------------------
    # Check at least one parameter
    # --------------------------------------------------------

    if name is None and course is None:

        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": (
                    "Please provide at least one search "
                    "parameter: name or course"
                ),
                "error": "Missing search parameter",
                "allowed_parameters": [
                    "name",
                    "course"
                ]
            }
        )

    # --------------------------------------------------------
    # Check empty name
    # --------------------------------------------------------

    if name is not None and not name.strip():

        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": "Name search parameter cannot be empty",
                "error": "Invalid name parameter"
            }
        )

    # --------------------------------------------------------
    # Check empty course
    # --------------------------------------------------------

    if course is not None and not course.strip():

        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": "Course search parameter cannot be empty",
                "error": "Invalid course parameter"
            }
        )

    # --------------------------------------------------------
    # Search MongoDB
    # --------------------------------------------------------

    matching_students = await search_students(
        name=name,
        course=course
    )

    # --------------------------------------------------------
    # No matching students
    # --------------------------------------------------------

    if not matching_students:

        search_details = {}

        if name is not None:
            search_details["name"] = name.strip()

        if course is not None:
            search_details["course"] = course.strip()

        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": (
                    "No student found matching "
                    "the given search criteria"
                ),
                "error": "Student not found",
                "search": search_details
            }
        )

    # --------------------------------------------------------
    # Search details
    # --------------------------------------------------------

    search_details = {}

    if name is not None:
        search_details["name"] = name.strip()

    if course is not None:
        search_details["course"] = course.strip()

    return {
        "status": "success",
        "message": "Matching students found",
        "count": len(matching_students),
        "search": search_details,
        "data": matching_students
    }


# ============================================================
# GET STUDENT BY ID
# ============================================================

@router.get("/students/{student_id}")
async def get_student_by_id_endpoint(
    student_id: int
):

    student = await get_student_by_id(
        student_id
    )

    if student is None:

        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": (
                    f"Student with ID {student_id} "
                    "was not found"
                ),
                "error": "Student not found"
            }
        )

    return {
        "status": "success",
        "message": "Student found successfully",
        "data": student
    }


# ============================================================
# UPDATE STUDENT
# ============================================================

@router.put("/students/update/{student_id}")
async def update_student_endpoint(
    student_id: int,
    updated_student: Student
):

    # --------------------------------------------------------
    # Check URL ID and body ID
    # --------------------------------------------------------

    if student_id != updated_student.id:

        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": (
                    f"Student ID in URL ({student_id}) "
                    f"does not match the student ID "
                    f"in request body ({updated_student.id})"
                ),
                "error": "ID mismatch"
            }
        )

    # --------------------------------------------------------
    # Check student exists
    # --------------------------------------------------------

    if not await student_exists(student_id):

        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": (
                    f"Cannot update student with ID "
                    f"{student_id} because the student "
                    "was not found"
                ),
                "error": "Student not found"
            }
        )

    # --------------------------------------------------------
    # Convert model
    # --------------------------------------------------------

    student_data = updated_student.model_dump()

    # --------------------------------------------------------
    # Update MongoDB
    # --------------------------------------------------------

    updated_data = await update_student(
        student_id,
        student_data
    )

    return {
        "status": "success",
        "message": "Student updated successfully",
        "data": updated_data
    }


# ============================================================
# DELETE STUDENT
# ============================================================

@router.delete("/students/delete/{student_id}")
async def delete_student_endpoint(
    student_id: int
):

    # --------------------------------------------------------
    # Delete student
    # --------------------------------------------------------

    deleted_student = await delete_student(
        student_id
    )

    # --------------------------------------------------------
    # Student not found
    # --------------------------------------------------------

    if deleted_student is None:

        raise HTTPException(
            status_code=404,
            detail={
                "status": "error",
                "message": (
                    f"Cannot delete student with ID "
                    f"{student_id} because the student "
                    "was not found"
                ),
                "error": "Student not found"
            }
        )

    return {
        "status": "success",
        "message": "Student deleted successfully",
        "data": deleted_student
    }