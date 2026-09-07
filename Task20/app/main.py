from fastapi import FastAPI

from app.routes.agent import router as agent_router


app = FastAPI(
    title="Task 20 - Goal Based AI Agent",
    description=(
        "Goal-based AI Agent using FastAPI, "
        "OpenRouter and backend tools."
    ),
    version="1.0.0"
)


app.include_router(
    agent_router
)


@app.get("/")
def root():

    return {
        "success": True,
        "message": (
            "Task 20 Goal-Based AI Agent is running."
        )
    }