from fastapi import FastAPI

from app.routes.chat import router as chat_router


app = FastAPI(
    title="Context-Aware AI Chat Assistant",
    description="FastAPI chatbot with session-based conversation memory",
    version="1.0.0"
)


app.include_router(chat_router)


@app.get("/")
def root():
    return {
        "success": True,
        "status_code": 200,
        "message": "Context-Aware AI Chat Assistant is running"
    }