from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import (
    APP_NAME,
    APP_VERSION,
)
from app.database import (
    close_mongodb_connection,
    connect_to_mongodb,
)
from app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs when the FastAPI application starts and stops.
    """

    await connect_to_mongodb()

    yield

    await close_mongodb_connection()


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "Task24 AI Observability API with OpenRouter "
        "and MongoDB Atlas."
    ),
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)