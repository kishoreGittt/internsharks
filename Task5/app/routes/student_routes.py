from fastapi import APIRouter, HTTPException, Query, status
from pydantic import EmailStr

from app.models.student import Student

from app.services.student_service import (
    create_student,
    student_exists,
    get_all_students,
    get_student_by_id,
    update_student,
    delete_student,
    delete_all_students,
    search_students
)


# ============================================================
# Router
# ============================================================

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


# ============================================================
# CREATE STUDENT
# ============================================================

@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED
)
async def create_student_endpoint(student: Student):

    try:

        # Check duplicate ID
        exists = await student_exists(student.id)

        if exists:

            raise HTTPException(
                status_code=409,
                detail={
                    "status": "error",
                    "error_code": 409,
                    "message": f"Student with ID {student.id} already exists",
                    "data": None
                }
            )

        student_data = student.model_dump()

        created_student = await create_student(
            student_data
        )

        return {
            "status": "success",
            "error_code": 0,
            "message": "Student created successfully",
            "data": created_student
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_code": 500,
                "message": "Failed to create student",
                "data": None,
                "details": str(e)
            }
        )


# ============================================================
# GET ALL STUDENTS
# ============================================================

@router.get("/")
async def get_all_students_endpoint():

    try:

        students = await get_all_students()

        if not students:

            return {
                "status": "success",
                "error_code": 0,
                "message": "No students found",
                "data": []
            }

        return {
            "status": "success",
            "error_code": 0,
            "message": "Students retrieved successfully",
            "data": students
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_code": 500,
                "message": "Failed to retrieve students",
                "data": None,
                "details": str(e)
            }
        )


# ============================================================
# GET STUDENT BY ID
# ============================================================

@router.get("/{student_id}")
async def get_student_by_id_endpoint(student_id: int):

    try:

        student = await get_student_by_id(
            student_id
        )

        if student is None:

            raise HTTPException(
                status_code=404,
                detail={
                    "status": "error",
                    "error_code": 404,
                    "message": f"Student with ID {student_id} not found",
                    "data": None
                }
            )

        return {
            "status": "success",
            "error_code": 0,
            "message": "Student retrieved successfully",
            "data": student
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_code": 500,
                "message": "Failed to retrieve student",
                "data": None,
                "details": str(e)
            }
        )


# ============================================================
# UPDATE STUDENT
# ============================================================

@router.put("/{student_id}")
async def update_student_endpoint(
    student_id: int,
    student: Student
):

    try:

        # Make sure the ID in URL and body match
        if student_id != student.id:

            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "error_code": 400,
                    "message": "Student ID in URL and request body must match",
                    "data": None
                }
            )

        exists = await student_exists(
            student_id
        )

        if not exists:

            raise HTTPException(
                status_code=404,
                detail={
                    "status": "error",
                    "error_code": 404,
                    "message": f"Student with ID {student_id} not found",
                    "data": None
                }
            )

        student_data = student.model_dump()

        updated_student = await update_student(
            student_id,
            student_data
        )

        return {
            "status": "success",
            "error_code": 0,
            "message": "Student updated successfully",
            "data": updated_student
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_code": 500,
                "message": "Failed to update student",
                "data": None,
                "details": str(e)
            }
        )


# ============================================================
# DELETE ALL STUDENTS
# ============================================================

@router.delete("/delete/all")
async def delete_all_students_endpoint():

    try:

        deleted_count = await delete_all_students()

        if deleted_count == 0:

            return {
                "status": "success",
                "error_code": 0,
                "message": "No students available to delete",
                "data": {
                    "deleted_count": 0
                }
            }

        return {
            "status": "success",
            "error_code": 0,
            "message": "All students deleted successfully",
            "data": {
                "deleted_count": deleted_count
            }
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_code": 500,
                "message": "Failed to delete students",
                "data": None,
                "details": str(e)
            }
        )


# ============================================================
# DELETE STUDENT BY ID
# ============================================================

@router.delete("/delete/{student_id}")
async def delete_student_endpoint(student_id: int):

    try:

        deleted_student = await delete_student(
            student_id
        )

        if deleted_student is None:

            raise HTTPException(
                status_code=404,
                detail={
                    "status": "error",
                    "error_code": 404,
                    "message": f"Student with ID {student_id} not found",
                    "data": None
                }
            )

        return {
            "status": "success",
            "error_code": 0,
            "message": "Student deleted successfully",
            "data": deleted_student
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_code": 500,
                "message": "Failed to delete student",
                "data": None,
                "details": str(e)
            }
        )


# ============================================================
# SEARCH STUDENTS
# ============================================================

@router.get("/search")
async def search_students_endpoint(
    name: str | None = Query(
        default=None,
        description="Search students by name"
    ),
    course: str | None = Query(
        default=None,
        description="Search/filter students by course"
    )
):

    try:

        # No search parameters
        if name is None and course is None:

            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "error_code": 400,
                    "message": "Provide at least one search parameter: name or course",
                    "data": None
                }
            )

        students = await search_students(
            name=name,
            course=course
        )

        if not students:

            search_conditions = {}

            if name is not None:
                search_conditions["name"] = name

            if course is not None:
                search_conditions["course"] = course

            return {
                "status": "success",
                "error_code": 0,
                "message": "No students matched the search criteria",
                "data": [],
                "search": search_conditions
            }

        return {
            "status": "success",
            "error_code": 0,
            "message": "Students matched the search criteria",
            "data": students
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_code": 500,
                "message": "Failed to search students",
                "data": None,
                "details": str(e)
            }
        )