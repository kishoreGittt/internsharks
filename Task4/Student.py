from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
import json
import os


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="Student Management API",
    description="Student CRUD API with JSON File Persistence and Search",
    version="4.0.0"
)


# ============================================================
# Pydantic Model
# ============================================================

class Student(BaseModel):
    id: int
    name: str
    email: EmailStr
    course: str


# ============================================================
# JSON File Configuration
# ============================================================

FILE_NAME = "students.json"


# ============================================================
# Custom Validation Error Handler
# ============================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):

    errors = []

    for error in exc.errors():

        field = " -> ".join(str(item) for item in error["loc"])

        if error["type"] == "missing":
            message = f"{field} is required"

        elif error["type"] == "int_parsing":
            message = f"{field} must be a number"

        elif error["type"] == "value_error":
            message = f"{field} contains an invalid value"

        else:
            message = error["msg"]

        errors.append({
            "field": field,
            "message": message
        })

    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "Request validation failed",
            "error": "Invalid input data",
            "details": errors
        }
    )


# ============================================================
# Load Students from JSON File
# ============================================================

def load_students():

    try:

        # Check whether the JSON file exists
        if not os.path.exists(FILE_NAME):

            # Create an empty JSON file
            with open(FILE_NAME, "w") as file:
                json.dump([], file, indent=4)

            return []

        # Open JSON file in read mode
        with open(FILE_NAME, "r") as file:

            data = json.load(file)

            # Make sure JSON contains a list
            if not isinstance(data, list):

                print(
                    "ERROR: students.json must contain a JSON array."
                )

                return []

            return data

    except json.JSONDecodeError:

        print(
            "ERROR: students.json contains invalid JSON data."
        )

        return []

    except PermissionError:

        print(
            "ERROR: Permission denied while reading students.json."
        )

        return []

    except Exception as e:

        print(
            f"ERROR: Unable to load student data: {str(e)}"
        )

        return []


# ============================================================
# Save Students to JSON File
# ============================================================

def save_students():

    try:

        # Open JSON file in write mode
        with open(FILE_NAME, "w") as file:

            # Convert Python list to JSON
            json.dump(
                students,
                file,
                indent=4
            )

        return True

    except PermissionError:

        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Unable to save student data because file permission was denied",
                "error": "File permission error"
            }
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Unable to save student data",
                "error": str(e)
            }
        )


# ============================================================
# Load Existing Students When Application Starts
# ============================================================

students = load_students()


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "status": "success",
        "message": "Student Management API is running",
        "version": "4.0.0",
        "storage": "JSON file"
    }


# ============================================================
# CREATE STUDENT
# ============================================================

@app.post("/students", status_code=201)
def create_student(student: Student):

    # --------------------------------------------------------
    # Check duplicate ID
    # --------------------------------------------------------

    for existing_student in students:

        if existing_student["id"] == student.id:

            raise HTTPException(
                status_code=409,
                detail={
                    "status": "error",
                    "message": f"Student with ID {student.id} already exists",
                    "error": "Duplicate student ID"
                }
            )

    # --------------------------------------------------------
    # Convert Pydantic model to dictionary
    # --------------------------------------------------------

    student_data = student.model_dump()

    # --------------------------------------------------------
    # Add student to Python list
    # --------------------------------------------------------

    students.append(student_data)

    # --------------------------------------------------------
    # Save updated list to JSON file
    # --------------------------------------------------------

    save_students()

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "status": "success",
        "message": "Student added successfully",
        "data": student_data
    }


# ============================================================
# GET ALL STUDENTS
# ============================================================

@app.get("/students")
def get_students():

    return {
        "status": "success",
        "message": "Students retrieved successfully",
        "count": len(students),
        "data": students
    }


# ============================================================
# GET STUDENT BY ID
# ============================================================

@app.get("/students/{student_id}")
def get_student(student_id: int):

    # --------------------------------------------------------
    # Search student
    # --------------------------------------------------------

    for student in students:

        if student["id"] == student_id:

            return {
                "status": "success",
                "message": "Student found successfully",
                "data": student
            }

    # --------------------------------------------------------
    # Student not found
    # --------------------------------------------------------

    raise HTTPException(
        status_code=404,
        detail={
            "status": "error",
            "message": f"Student with ID {student_id} was not found",
            "error": "Student not found"
        }
    )


# ============================================================
# UPDATE STUDENT
# ============================================================

@app.put("/students/{student_id}")
def update_student(
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
                    f"Student ID in URL ({student_id}) does not "
                    f"match the student ID in request body "
                    f"({updated_student.id})"
                ),
                "error": "ID mismatch"
            }
        )

    # --------------------------------------------------------
    # Find student
    # --------------------------------------------------------

    for index, student in enumerate(students):

        if student["id"] == student_id:

            # Convert updated Pydantic model to dictionary
            student_data = updated_student.model_dump()

            # Update student
            students[index] = student_data

            # Save updated data to JSON
            save_students()

            return {
                "status": "success",
                "message": "Student updated successfully",
                "data": student_data
            }

    # --------------------------------------------------------
    # Student not found
    # --------------------------------------------------------

    raise HTTPException(
        status_code=404,
        detail={
            "status": "error",
            "message": (
                f"Cannot update student with ID "
                f"{student_id} because the student was not found"
            ),
            "error": "Student not found"
        }
    )


# ============================================================
# DELETE STUDENT
# ============================================================

@app.delete("/students/{student_id}")
def delete_student(student_id: int):

    # --------------------------------------------------------
    # Find student
    # --------------------------------------------------------

    for index, student in enumerate(students):

        if student["id"] == student_id:

            # Remove student
            deleted_student = students.pop(index)

            # Save changes to JSON
            save_students()

            return {
                "status": "success",
                "message": "Student deleted successfully",
                "data": deleted_student
            }

    # --------------------------------------------------------
    # Student not found
    # --------------------------------------------------------

    raise HTTPException(
        status_code=404,
          detail={ 
            "status": "error",
            "message": (
                f"Cannot delete student with ID "
                f"{student_id} because the student was not found"
            ),
            "error": "Student not found"
        }
    )


# ============================================================
# SEARCH STUDENTS
# ============================================================

@app.get("/students/search")
def search_students(
    name: str | None = Query(default=None),
    course: str | None = Query(default=None)
):

    # --------------------------------------------------------
    # Check if search parameters are provided
    # --------------------------------------------------------

    if name is None and course is None:

        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": (
                    "Please provide at least one search parameter: "
                    "name or course"
                ),
                "error": "Missing search parameter"
            }
        )

    # --------------------------------------------------------
    # Start with all students
    # --------------------------------------------------------

    matching_students = students

    # --------------------------------------------------------
    # Search by name
    # --------------------------------------------------------

    if name is not None:

        matching_students = [
            student
            for student in matching_students
            if name.lower() in student["name"].lower()
        ]

    # --------------------------------------------------------
    # Search by course
    # --------------------------------------------------------

    if course is not None:

        matching_students = [
            student
            for student in matching_students
            if course.lower() in student["course"].lower()
        ]

    # --------------------------------------------------------
    # No matching students
    # --------------------------------------------------------

    if not matching_students:

        search_details = {}

        if name is not None:
            search_details["name"] = name

        if course is not None:
            search_details["course"] = course

        return {
            "status": "success",
            "message": "No students matched the given search criteria",
            "count": 0,
            "search": search_details,
            "data": []
        }

    # --------------------------------------------------------
    # Matching students found
    # --------------------------------------------------------

    return {
        "status": "success",
        "message": "Matching students found",
        "count": len(matching_students),
        "data": matching_students
    }