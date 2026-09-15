from fastapi import FastAPI

from app.routes.agent import router as agent_router


app = FastAPI(
    title="Task 21 - Stateful AI Agent",
    version="1.0.0"
)


app.include_router(agent_router)


@app.get("/")
async def root():

    return {
        "success": True,
        "message": "Task 21 Stateful AI Agent API"
    }


@app.get("/health")
async def health():

    return {
        "success": True,
        "status": "healthy"
    }