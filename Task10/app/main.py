from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.mongodb import (
    connect_to_mongodb,
    close_mongodb_connection
)

from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.routes.tasks import router as tasks_router
from app.routes.admin import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongodb()

    yield

    await close_mongodb_connection()


app = FastAPI(
    title="Task Management API",
    description="Production-style Task Management Backend",
    version="1.0.0",
    lifespan=lifespan
)


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tasks_router)
app.include_router(admin_router)


@app.get("/")
async def root():
    return {
        "success": True,
        "message": "Task Management API is running"
    }