from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.database.mongodb import (
    connect_database,
    close_database
)

from app.routes.auth_routes import router as auth_router
from app.routes.user_routes import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    await connect_database()

    yield

    await close_database()


app = FastAPI(
    title="Task 9 - JWT Refresh Token Authentication",
    description="FastAPI JWT Authentication with Access Tokens, Refresh Tokens and Token Revocation",
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================
# VALIDATION ERROR
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
            "errors": exc.errors()
        }
    )


# ============================================================
# GENERAL ERROR
# ============================================================

@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception
):

    print(f"Internal server error: {type(exc).__name__}")

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An internal server error occurred"
        }
    )


# ============================================================
# ROUTES
# ============================================================

app.include_router(auth_router)
app.include_router(user_router)


@app.get("/")
async def root():

    return {
        "success": True,
        "message": "Task 9 Authentication API is running"
    }