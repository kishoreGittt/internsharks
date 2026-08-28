from fastapi import FastAPI

from app.routes.ai import router as ai_router


app = FastAPI(
    title="Task 13 - Structured AI API",
    description="AI text analysis using OpenRouter",
    version="1.0.0"
)


app.include_router(ai_router)


@app.get("/")
async def root():

    return {
        "success": True,
        "status_code": 200,
        "message": "Task 13 Structured AI API is running"
    }