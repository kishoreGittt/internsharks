from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routes.vision import router as vision_router


app = FastAPI(
    title="Task 25 - Multimodal AI Backend",
    description="Multimodal image analysis using OpenRouter vision model",
    version="1.0.0",
)


def get_error_code(
    status_code: int,
    detail: object,
) -> str:
    """
    Return a symbolic error code based on the error.
    """

    if isinstance(detail, dict):
        custom_code = detail.get("error_code")

        if custom_code:
            return str(custom_code)

    error_codes = {
        400: "BAD_REQUEST",
        401: "AUTHENTICATION_FAILED",
        403: "FORBIDDEN",
        404: "ROUTE_NOT_FOUND",
        413: "IMAGE_TOO_LARGE",
        415: "UNSUPPORTED_MEDIA_TYPE",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_SERVER_ERROR",
        502: "EXTERNAL_AI_SERVICE_ERROR",
        503: "SERVICE_UNAVAILABLE",
        504: "AI_SERVICE_TIMEOUT",
    }

    return error_codes.get(
        status_code,
        "UNKNOWN_ERROR",
    )


def get_error_message(detail: object) -> str:
    """
    Convert FastAPI error detail into a readable message.
    """

    if isinstance(detail, dict):
        return str(
            detail.get(
                "message",
                "An error occurred",
            )
        )

    if isinstance(detail, list):
        return "Request validation failed"

    return str(detail)


@app.get("/")
async def root():
    return {
        "success": True,
        "status_code": 200,
        "error_code": None,
        "message": "Task25 application is running",
    }


@app.get("/health")
async def health():
    return {
        "success": True,
        "status_code": 200,
        "error_code": None,
        "message": "Service is healthy",
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    error_code = get_error_code(
        status_code=exc.status_code,
        detail=exc.detail,
    )

    message = get_error_message(
        detail=exc.detail,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "status_code": exc.status_code,
            "error_code": error_code,
            "message": message,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "status_code": 422,
            "error_code": "VALIDATION_ERROR",
            "message": "Request validation failed",
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception,
):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "status_code": 500,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected internal server error occurred",
        },
    )


app.include_router(vision_router)