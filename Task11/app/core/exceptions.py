import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


logger = logging.getLogger(__name__)


ERROR_NAMES = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
    500: "INTERNAL_SERVER_ERROR",
    503: "SERVICE_UNAVAILABLE",
}


def error_response(
    status_code: int,
    error: str,
    message: str
) -> JSONResponse:

    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "status_code": status_code,
            "error": error,
            "message": message,
        },
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
):
    status_code = exc.status_code

    detail = exc.detail

    if isinstance(detail, str):
        message = detail
    else:
        message = "Request could not be processed"

    error_name = ERROR_NAMES.get(
        status_code,
        "HTTP_ERROR"
    )

    return error_response(
        status_code=status_code,
        error=error_name,
        message=message,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return error_response(
        status_code=422,
        error="VALIDATION_ERROR",
        message="Invalid request data",
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
):
    logger.exception(
        "Unexpected application error: %s %s",
        request.method,
        request.url.path,
    )

    return error_response(
        status_code=500,
        error="INTERNAL_SERVER_ERROR",
        message="An unexpected internal server error occurred",
    )