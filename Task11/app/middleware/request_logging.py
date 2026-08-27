import logging
import time

from fastapi import Request


logger = logging.getLogger("request")


async def request_logging_middleware(
    request: Request,
    call_next
):
    start_time = time.perf_counter()

    try:
        response = await call_next(request)

        status_code = response.status_code

        return response

    except Exception:
        status_code = 500
        raise

    finally:
        processing_time = (
            time.perf_counter() - start_time
        ) * 1000

        logger.info(
            "%s %s - %s - %.2fms",
            request.method,
            request.url.path,
            status_code,
            processing_time,
        )