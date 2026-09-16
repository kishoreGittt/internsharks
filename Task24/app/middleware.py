import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.tracing import generate_trace_id

logger = logging.getLogger("task24.request")

class RequestTrackingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = generate_trace_id()
        request.state.trace_id = trace_id
        start = time.perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["X-Trace-ID"] = trace_id
            return response
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.info(
                "http_request_completed trace_id=%s method=%s path=%s status_code=%s duration_ms=%.2f",
                trace_id, request.method, request.url.path, status_code, duration_ms,
            )
