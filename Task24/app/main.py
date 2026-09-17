from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import APP_NAME
from app.database import (
    close_mongodb,
    connect_to_mongodb,
)
from app.logging_config import configure_logging
from app.middleware import RequestTrackingMiddleware
from app.routes import router
from app.tracing import TraceManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()

    await connect_to_mongodb()

    yield

    await close_mongodb()


app = FastAPI(
    title=APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    RequestTrackingMiddleware
)

app.include_router(router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    trace_id = getattr(
        request.state,
        "trace_id",
        None,
    )

    trace = TraceManager(
        trace_id=trace_id
    )

    span = trace.start_span(
        "request_validation"
    )

    trace.finish_span(
        span,
        status="failed",
        error_category="VALIDATION_ERROR",
    )

    try:
        await trace.save_trace(
            request_type=request.method.lower(),
            model="not_called",
            prompt_version="unknown",
            status="validation_failed",
            error_category="VALIDATION_ERROR",
            status_code=422,
        )
    except Exception:
        pass

    return JSONResponse(
        status_code=422,
        headers={
            "X-Trace-ID": trace.trace_id
        },
        content={
            "success": False,
            "status_code": 422,
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed.",
            "trace_id": trace.trace_id,
        },
    )