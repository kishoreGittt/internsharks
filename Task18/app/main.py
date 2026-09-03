from fastapi import FastAPI

from app.routes.assistant import router


app = FastAPI(
    title="AI Tool Calling Assistant",
    description=(
        "FastAPI AI assistant using Gemini "
        "function calling"
    ),
    version="1.0.0"
)


app.include_router(router)


@app.get("/")
def root():

    return {
        "message": "AI Tool Calling Assistant is running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }