from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routes.student_routes import router


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="Student Management API",
    description="Student CRUD API with MongoDB and Search",
    version="5.0.0"
)


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

        field = " -> ".join(
            str(item)
            for item in error["loc"]
        )

        if error["type"] == "missing":

            message = f"{field} is required"

        elif error["type"] == "int_parsing":

            message = f"{field} must be a number"

        elif error["type"] == "value_error.email":

            message = (
                f"{field} must be a valid email address"
            )

        elif error["type"] == "value_error":

            message = (
                f"{field} contains an invalid value"
            )

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
# HOME ENDPOINT
# ============================================================

@app.get("/")
async def home_endpoint():

    return {
        "status": "success",
        "message": "Student Management API is running",
        "version": "5.0.0",
        "storage": "MongoDB"
    }


# ============================================================
# Register Student Routes
# ============================================================

app.include_router(router)