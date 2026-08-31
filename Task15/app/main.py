from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routes.summarizer import (
    router as summarizer_router
)

from app.routes.document import (
    router as document_router
)


app = FastAPI(
    title="AI Document Summarization API",
    description="AI-powered text and document summarization API",
    version="1.0.0"
)


# Handle FastAPI validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "status_code": 422,
            "error": "VALIDATION_ERROR",
            "message": "Invalid request data"
        }
    )


# Handle HTTPException
@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception
):

    # Let HTTPException be handled separately by FastAPI
    from fastapi import HTTPException

    if isinstance(exc, HTTPException):

        detail = exc.detail

        if isinstance(detail, dict):

            error = detail.get(
                "error",
                "REQUEST_ERROR"
            )

            message = detail.get(
                "message",
                "Request failed"
            )

        else:

            error = "REQUEST_ERROR"
            message = str(detail)

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "status_code": exc.status_code,
                "error": error,
                "message": message
            }
        )

    # Hide unexpected internal errors
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "status_code": 500,
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An internal server error occurred"
        }
    )


app.include_router(summarizer_router)
app.include_router(document_router)


@app.get("/")
async def root():

    return {
        "success": True,
        "status_code": 200,
        "message": "AI Summarization API is running"
    }


@app.get("/health")
async def health():

    return {
        "success": True,
        "status_code": 200,
        "message": "API is healthy"
    }