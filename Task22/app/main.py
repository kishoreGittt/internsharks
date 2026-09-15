from fastapi import FastAPI

from app.routes.agent import router as agent_router


app = FastAPI(
    title="Task 22 - Resilient AI Agent",
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "message": "Task 22 Resilient AI Agent is running"
    }


app.include_router(agent_router)