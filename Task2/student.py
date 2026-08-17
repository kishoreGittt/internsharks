from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr


app = FastAPI()


# Student model
class Student(BaseModel):
    id: int
    name: str
    email: EmailStr
    course: str


# In-memory list
students = []


# 1. POST - Add Student
@app.post("/students", status_code=status.HTTP_201_CREATED)
def add_student(student: Student):

    students.append(student)

    return {
        "success": True,
        "message": "Student added successfully",
        "data": student
    }


# 2. GET - Get All Students
@app.get("/students")
def get_students():

    return {
        "success": True,
        "message": "Students fetched successfully",
        "data": students
    }


# 3. GET - Get Student By ID
@app.get("/students/{student_id}")
def get_student(student_id: int):

    for student in students:

        if student.id == student_id:
            return {
                "success": True,
                "message": "Student found",
                "data": student
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Student not found"
    )


# 4. PUT - Update Student
@app.put("/students/{student_id}")
def update_student(student_id: int, updated_student: Student):

    for index, student in enumerate(students):

        if student.id == student_id:

            students[index] = updated_student

            return {
                "success": True,
                "message": "Student updated successfully",
                "data": updated_student
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Student not found"
    )


# 5. DELETE - Delete Student
@app.delete("/students/{student_id}")
def delete_student(student_id: int):

    for student in students:

        if student.id == student_id:

            students.remove(student)

            return {
                "success": True,
                "message": "Student deleted successfully",
                "data": student
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Student not found"
    )