from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.database.mongodb import (
    connect_to_mongodb,
    close_mongodb_connection
)

from app.routes.auth import router as auth_router
from app.routes.user import router as user_router


# ============================================================
# Application Lifespan
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    await connect_to_mongodb()

    yield

    await close_mongodb_connection()


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="Task 7 - JWT Authentication API",
    description="FastAPI JWT Authentication with MongoDB",
    version="1.0.0",
    lifespan=lifespan
)


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
            "details": exc.errors()
        }
    )


# ============================================================
# General Exception Handler
# ============================================================

@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception
):

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred"
        }
    )


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
async def root():

    return {
        "success": True,
        "message": "Task 7 JWT Authentication API is running"
    }


# ============================================================
# Include Routers
# ============================================================

app.include_router(auth_router)
app.include_router(user_router)