from fastapi import FastAPI

from app.routes.ai import router as ai_router


app = FastAPI(
    title="Task 12 - AI Text Assistant API",
    description="FastAPI application integrated with Groq AI",
    version="1.0.0"
)


app.include_router(ai_router)


@app.get("/")
async def root():
    return {
        "success": True,
        "status_code": 200,
        "message": "AI Text Assistant API is running"
    }