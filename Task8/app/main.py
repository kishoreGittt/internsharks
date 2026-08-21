from fastapi import FastAPI

from app.database.mongodb import (
    connect_to_mongodb,
    close_mongodb
)

from app.routes.auth import (
    router as auth_router
)

from app.routes.user import (
    router as user_router
)

from app.routes.admin import (
    router as admin_router
)


app = FastAPI(

    title="Task 8 - RBAC User Management API",

    description=(
        "JWT Authentication, "
        "MongoDB User Management "
        "and Role-Based Access Control"
    ),

    version="1.0.0"
)


# ============================================================
# STARTUP
# ============================================================

@app.on_event(
    "startup"
)
async def startup():

    await connect_to_mongodb()


# ============================================================
# SHUTDOWN
# ============================================================

@app.on_event(
    "shutdown"
)
async def shutdown():

    await close_mongodb()


# ============================================================
# ROUTES
# ============================================================

app.include_router(
    auth_router
)

app.include_router(
    user_router
)

app.include_router(
    admin_router
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
async def root():

    return {

        "success": True,

        "message": "Task 8 RBAC API is running"
    }