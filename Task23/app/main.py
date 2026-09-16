from fastapi import FastAPI
from app.config import settings
from app.routes.eval import router
from app.storage.database import init_db

app = FastAPI(title=settings.app_name, version="1.0.0")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return {"success": True, "message": "Task 23 LLM Evaluation API is running"}

app.include_router(router)
