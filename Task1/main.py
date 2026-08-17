from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import re


app = FastAPI(
    title="Python API Task 1",
    description="Simple POST API with JSON validation",
    version="1.0.0",
)


# Handle unexpected errors
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
        },
    )


# Home endpoint
@app.get("/")
async def home():
    return {
        "success": True,
        "message": "Task 1 is running",
        "docs": "/docs",
    }


# Create user endpoint
@app.post("/users", status_code=201)
async def create_user(request: Request):

    # Read JSON request body
    data = await request.json()

    # Check for missing fields
    required_fields = ["name", "email", "age"]

    missing_fields = [
        field for field in required_fields
        if field not in data
    ]

    if missing_fields:
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": "Missing required fields",
                "errors": missing_fields,
            },
        )

    # Get values
    name = data["name"]
    email = data["email"]
    age = data["age"]

    # Validate name
    if not isinstance(name, str) or not name.strip():
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": "Name must be a valid string",
            },
        )

    # Validate email
    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    if not isinstance(email, str) or not re.match(email_pattern, email):
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": "Invalid email address",
            },
        )

    # Validate age
    if not isinstance(age, int) or isinstance(age, bool) or age < 18:
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": "Age must be 18 or above",
            },
        )

    # Successful response
    return {
        "success": True,
        "message": "User created successfully",
        "data": {
            "name": name,
            "email": email,
            "age": age,
        },
    }