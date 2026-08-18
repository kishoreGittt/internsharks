from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routes.student_routes import router


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="Student Management API",
    description="Student CRUD API with MongoDB, Search and Filtering",
    version="5.0.0"
)


# ============================================================
# Validation Error Handler
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

        message = error["msg"]

        errors.append({
            "field": field,
            "message": message
        })

    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "error_code": 422,
            "message": "Request validation failed",
            "data": errors
        }
    )


# ============================================================
# Global HTTP Exception Handler
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error_code": 500,
            "message": "Internal server error",
            "data": None
        }
    )


# ============================================================
# Home Endpoint
# ============================================================

@app.get("/")
async def home_endpoint():

    return {
        "status": "success",
        "error_code": 0,
        "message": "Student Management API is running",
        "data": {
            "version": "5.0.0",
            "storage": "MongoDB"
        }
    }


# ============================================================
# Register Student Routes
# ============================================================

app.include_router(router)