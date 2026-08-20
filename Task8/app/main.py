from fastapi import FastAPI

from app.routes.auth import router as auth_router
from app.routes.user import router as user_router
from app.routes.admin import router as admin_router


app = FastAPI(
    title="Task 8 - RBAC User Management API",
    description=(
        "FastAPI JWT Authentication with "
        "MongoDB and Role-Based Access Control"
    ),
    version="8.0.0"
)


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(admin_router)


@app.get("/")
async def root():

    return {
        "success": True,
        "message": "Task 8 RBAC API is running",
        "data": {
            "authentication": "JWT",
            "authorization": "RBAC",
            "roles": [
                "user",
                "admin"
            ]
        }
    }