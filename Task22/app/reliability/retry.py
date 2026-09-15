import time
import random
from app.config import MAX_RETRIES, RETRY_BASE_DELAY, ENABLE_JITTER
from app.reliability.errors import AgentError

def retry_call(operation, *, max_retries=MAX_RETRIES, base_delay=RETRY_BASE_DELAY,
               on_attempt=None):
    last_error = None

    for attempt in range(1, max_retries + 1):
        if on_attempt:
            on_attempt(attempt)

        try:
            return operation(attempt)
        except Exception as exc:
            last_error = exc
            retryable = isinstance(exc, AgentError) and exc.retryable

            if not retryable or attempt >= max_retries:
                raise

            delay = base_delay * (2 ** (attempt - 1))
            if ENABLE_JITTER:
                delay += random.uniform(0, 0.25)
            time.sleep(delay)

    raise last_error
