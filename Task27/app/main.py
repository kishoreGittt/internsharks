import asyncio

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from fastapi.responses import JSONResponse

from app.config import settings

from app.auth.dependencies import (
    get_current_user
)

from app.routes.auth import (
    router as auth_router
)

from app.routes.chat import (
    router as chat_router
)

from app.routes.knowledge import (
    router as knowledge_router
)

from app.routes.vision import (
    router as vision_router
)

from app.routes.jobs import (
    router as jobs_router
)

from app.routes.observability import (
    router as observability_router
)

from app.routes.eval import (
    router as eval_router
)

from app.storage.mongodb import (
    create_indexes,
    ping_mongodb,
    close_mongodb,
    get_mongodb_status
)

from app.workers.document_worker import (
    worker_loop
)


# =========================================================
# APPLICATION LIFESPAN
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("\n==========================================")
    print("          STARTING TASK 27")
    print("==========================================")

    # -----------------------------------------------------
    # MongoDB connection
    # -----------------------------------------------------

    mongo_ok = await ping_mongodb()

    if not mongo_ok:

        print(
            "WARNING: MongoDB connection failed."
        )

        yield

        return

    print(
        "MongoDB connection successful."
    )

    # -----------------------------------------------------
    # MongoDB indexes
    # -----------------------------------------------------

    await create_indexes()

    print(
        "MongoDB indexes ready."
    )

    # -----------------------------------------------------
    # START DOCUMENT WORKER
    # -----------------------------------------------------

    worker_task = asyncio.create_task(
        worker_loop()
    )

    print(
        "Document worker task started."
    )

    print("==========================================\n")

    try:

        yield

    finally:

        # -------------------------------------------------
        # STOP DOCUMENT WORKER
        # -------------------------------------------------

        print(
            "Stopping document worker..."
        )

        worker_task.cancel()

        try:

            await worker_task

        except asyncio.CancelledError:

            pass

        # -------------------------------------------------
        # CLOSE MONGODB
        # -------------------------------------------------

        await close_mongodb()

        print(
            "MongoDB connection closed."
        )


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan
)


# =========================================================
# ROUTERS
# =========================================================

app.include_router(
    auth_router
)

app.include_router(
    chat_router
)

app.include_router(
    knowledge_router
)

app.include_router(
    vision_router
)

app.include_router(
    jobs_router
)

app.include_router(
    observability_router
)

app.include_router(
    eval_router
)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
async def root():

    return {
        "success": True,
        "status_code": 200,
        "message": (
            "Task 27 AI Knowledge & Operations "
            "Copilot is running"
        )
    }


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
async def health():

    mongo_status = await get_mongodb_status()

    if mongo_status["status"] != "healthy":

        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "status_code": 503,
                "error": "DATABASE_UNAVAILABLE",
                "message": "MongoDB is unavailable",
                "data": {
                    "api": "healthy",
                    "mongodb": mongo_status,
                    "redis": "not_used"
                }
            }
        )

    return {
        "success": True,
        "status_code": 200,
        "data": {
            "api": "healthy",
            "mongodb": mongo_status,
            "redis": "not_used"
        }
    }


# =========================================================
# CURRENT USER
# =========================================================

@app.get("/users/me")
async def users_me(
    current_user: dict = Depends(
        get_current_user
    )
):

    return {
        "success": True,
        "status_code": 200,
        "data": {
            "user_id": current_user.get(
                "user_id"
            ),
            "email": current_user.get(
                "email"
            ),
            "name": current_user.get(
                "name"
            ),
            "role": current_user.get(
                "role",
                "user"
            )
        }
    }