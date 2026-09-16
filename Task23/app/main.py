from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.routes.eval import router
from app.storage.database import mongo_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs when the FastAPI application starts and stops.
    """

    if not mongo_database.check_connection():
        print(
            "WARNING: MongoDB connection failed. "
            "Make sure MongoDB is running."
        )
    else:
        print("MongoDB connection successful.")

    yield

    mongo_database.close()
    print("MongoDB connection closed.")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "success": True,
        "status_code": 200,
        "message": "Task23 Evaluation API is running",
        "database": "MongoDB",
    }


@app.get("/health")
def health():
    mongo_status = mongo_database.check_connection()

    return {
        "success": mongo_status,
        "status_code": 200 if mongo_status else 503,
        "database": "MongoDB",
        "mongodb_connected": mongo_status,
    }