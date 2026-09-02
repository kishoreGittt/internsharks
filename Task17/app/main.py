from fastapi import FastAPI

from app.routes.rag import (
    router as rag_router
)


app = FastAPI(

    title="Task 17 - RAG Document Chat API",

    description=(
        "RAG API using FastAPI, "
        "Google Gemini and FAISS"
    ),

    version="1.0.0"
)


app.include_router(
    rag_router
)


@app.get("/")
def root():

    return {

        "success": True,

        "message":
            "Task 17 RAG API is running"

    }


@app.get("/health")
def health():

    return {

        "success": True,

        "status":
            "healthy"

    }