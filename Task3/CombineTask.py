from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr


app = FastAPI(
    title="Student Management API",
    description="Student CRUD API with Search and Filtering",
    version="3.0.0"
)


# ============================================================
# PYDANTIC MODEL
# ============================================================

class Student(BaseModel):
    id: int
    name: str
    email: EmailStr
    course: str


# ============================================================
# IN-MEMORY STUDENT STORAGE
# ============================================================

students = []


# ============================================================
# POST - ADD STUDENT
# ============================================================

@app.post("/students", status_code=201)
def create_student(student: Student):

    try:

        # Check whether student ID already exists
        for existing_student in students:

            if existing_student["id"] == student.id:

                raise HTTPException(
                    status_code=409,
                    detail="Student with this ID already exists"
                )

        # Add student to list
        students.append(student.model_dump())

        return {
            "status": "success",
            "message": "Student created successfully",
            "data": student
        }

    except HTTPException:
        raise

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


# ============================================================
# TASK 3 - SEARCH AND FILTER
# IMPORTANT:
# /students/search MUST COME BEFORE /students/{student_id}
# ============================================================


# ============================================================
# GET - SEARCH STUDENTS
# ============================================================

@app.get("/students/search")
def search_students(
    name: str | None = None,
    course: str | None = None
):

    try:

        # ----------------------------------------------------
        # Check whether at least one query parameter is given
        # ----------------------------------------------------

        if name is None and course is None:

            raise HTTPException(
                status_code=400,
                detail="Please provide name or course as a query parameter"
            )


        # ----------------------------------------------------
        # Start with all students
        # ----------------------------------------------------

        results = students.copy()


        # ----------------------------------------------------
        # Search students by name
        # ----------------------------------------------------

        if name:

            results = [
                student
                for student in results
                if name.lower() in student["name"].lower()
            ]


        # ----------------------------------------------------
        # Filter students by course
        # ----------------------------------------------------

        if course:

            results = [
                student
                for student in results
                if course.lower() in student["course"].lower()
            ]


        # ----------------------------------------------------
        # Check whether any student matched
        # ----------------------------------------------------

        if not results:

            return {
                "status": "success",
                "count": 0,
                "message": "No students matched the given search criteria"
                
            }


        # ----------------------------------------------------
        # Get only matching student IDs
        # ----------------------------------------------------

        student_ids = [
            student["id"]
            for student in results
        ]


        # ----------------------------------------------------
        # Return matching student IDs
        # ----------------------------------------------------

        return {
            "status": "success",
            "count": len(student_ids),
            "data": student_ids
        }


    except HTTPException:
        raise

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


# ============================================================
# GET - GET ALL STUDENTS
# ============================================================

@app.get("/students")
def get_students():

    try:

        return {
            "status": "success",
            "count": len(students),
            "data": students
        }

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


# ============================================================
# GET - GET STUDENT BY ID
# ============================================================

@app.get("/students/{student_id}")
def get_student(student_id: int):

    try:

        for student in students:

            if student["id"] == student_id:

                return {
                    "status": "success",
                    "data": student
                }


        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )


    except HTTPException:
        raise

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


# ============================================================
# PUT - UPDATE STUDENT
# ============================================================

@app.put("/students/{student_id}")
def update_student(
    student_id: int,
    updated_student: Student
):

    try:

        for index, student in enumerate(students):

            if student["id"] == student_id:

                students[index] = updated_student.model_dump()

                return {
                    "status": "success",
                    "message": "Student updated successfully",
                    "data": students[index]
                }


        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )


    except HTTPException:
        raise

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


# ============================================================
# DELETE - DELETE STUDENT
# ============================================================

@app.delete("/students/{student_id}")
def delete_student(student_id: int):

    try:

        for index, student in enumerate(students):

            if student["id"] == student_id:

                deleted_student = students.pop(index)

                return {
                    "status": "success",
                    "message": "Student deleted successfully",
                    "data": deleted_student
                }


        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )


    except HTTPException:
        raise

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )