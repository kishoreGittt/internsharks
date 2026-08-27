import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.exceptions import (
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.core.logging_config import configure_logging
from app.database.mongodb import (
    check_database_connection,
    close_database_connection,
    connect_to_database,
)
from app.middleware.request_logging import (
    request_logging_middleware,
)
from app.routes import admin, auth, tasks, users


configure_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info(
        "Application startup - environment=%s",
        settings.APP_ENV
    )

    try:
        await connect_to_database()

    except Exception:
        logger.exception(
            "Application startup failed because MongoDB is unavailable"
        )

        raise

    yield

    await close_database_connection()

    logger.info(
        "Application shutdown completed"
    )


app = FastAPI(
    title="Task Management API",
    version="1.0.0",
    lifespan=lifespan,
)


app.middleware("http")(
    request_logging_middleware
)


app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    Exception,
    general_exception_handler,
)


@app.get("/health")
async def health_check():

    database_connected = (
        await check_database_connection()
    )

    if not database_connected:

        return {
            "success": False,
            "status_code": 503,
            "status": "unhealthy",
            "database": "disconnected",
        }

    return {
        "success": True,
        "status_code": 200,
        "status": "healthy",
        "database": "connected",
    }


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tasks.router)
app.include_router(admin.router)