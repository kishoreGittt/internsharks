from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.mongodb import (
    connect_to_mongodb,
    close_mongodb,
    create_indexes
)

from app.routes.auth_routes import router as auth_router
from app.routes.user_routes import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    await connect_to_mongodb()
    await create_indexes()

    yield

    await close_mongodb()


app = FastAPI(
    title="Task 9 - JWT Refresh Token Authentication",
    description=(
        "FastAPI authentication system using short-lived "
        "access tokens and long-lived refresh tokens."
    ),
    version="1.0.0",
    lifespan=lifespan
)


app.include_router(auth_router)
app.include_router(user_router)


@app.get("/")
async def root():

    return {
        "success": True,
        "message": "Task 9 Authentication API is running",
        "data": None
    }