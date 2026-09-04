from fastapi import FastAPI

from app.routes.employee_assistant import (
    router
)


app = FastAPI(
    title="Task 19 - AI Employee Assistant",
    description=(
        "AI Employee Assistant using "
        "OpenRouter and multi-tool calling"
    ),
    version="1.0.0"
)


app.include_router(router)


@app.get("/")
def root():

    return {
        "success": True,
        "message":
            "Task 19 AI Employee Assistant is running."
    }


@app.get("/health")
def health():

    return {
        "success": True,
        "status": "healthy"
    }