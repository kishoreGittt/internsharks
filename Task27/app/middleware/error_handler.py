from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException


async def http_exception_handler(
    request: Request,
    exc: HTTPException
):

    detail = exc.detail

    if isinstance(
        detail,
        dict
    ):

        body = detail

    else:

        body = {
            "success": False,

            "status_code":
                exc.status_code,

            "error":
                "REQUEST_ERROR",

            "message":
                str(detail)
        }

    return JSONResponse(
        status_code=exc.status_code,
        content=body
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):

    return JSONResponse(

        status_code=422,

        content={

            "success": False,

            "status_code": 422,

            "error":
                "VALIDATION_ERROR",

            "message":
                "Request validation failed.",

            "details":
                exc.errors()
        }
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
):

    return JSONResponse(

        status_code=500,

        content={

            "success": False,

            "status_code": 500,

            "error":
                "INTERNAL_SERVER_ERROR",

            "message":
                "An unexpected server error occurred."
        }
    )