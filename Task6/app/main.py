from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.database.connection import (
    connect_to_mongodb,
    close_mongodb
)

from app.routes.auth import router as auth_router


# ============================================================
# Application Lifespan
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    # Startup
    await connect_to_mongodb()

    yield

    # Shutdown
    await close_mongodb()


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="Task 6 - User Authentication API",
    description=(
        "User Authentication API using FastAPI, "
        "MongoDB, Motor, Passlib and bcrypt"
    ),
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================
# Include Routes
# ============================================================

app.include_router(auth_router)


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
async def home():

    return {
        "success": True,
        "error_code": None,
        "message": "User Authentication API is running",
        "data": {
            "service": "Task 6 Authentication API",
            "docs": "/docs"
        }
    }


# ============================================================
# Validation Error Handler
# ============================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "data": {
                "errors": exc.errors()
            }
        }
    )


# ============================================================
# HTTP Exception Handler
# ============================================================

@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception
):

    print(f"Internal Server Error: {exc}")

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected server error occurred",
            "data": None
        }
    )