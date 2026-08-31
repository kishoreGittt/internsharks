from fastapi import FastAPI

from app.routes.summarizer import router as summarizer_router


app = FastAPI(
    title="Task 14 - AI Summarization API",
    description="AI-powered text summarization using FastAPI and OpenRouter",
    version="1.0.0"
)


app.include_router(summarizer_router)


@app.get("/")
async def root():

    return {
        "success": True,
        "status_code": 200,
        "message": "Task 14 AI Summarization API is running"
    }


@app.get("/health")
async def health_check():

    return {
        "success": True,
        "status_code": 200,
        "message": "API is healthy"
    }