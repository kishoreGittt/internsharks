import random
import time
from typing import Callable, Any

from app.reliability.errors import AgentError


def retry_with_backoff(
    operation: Callable[[], Any],
    max_retries: int = 3,
    base_delay: float = 1.0,
    jitter: bool = True,
    on_attempt: Callable[[int, str, str | None], None] | None = None,
):
    """
    Executes an operation with retry support.

    max_retries=3 means:
    - Attempt 1
    - Attempt 2
    - Attempt 3
    - Attempt 4 final attempt

    If you want exactly 3 total attempts, pass max_retries=2.
    """

    total_attempts = max_retries + 1
    last_error = None

    for attempt_number in range(1, total_attempts + 1):
        try:
            if on_attempt:
                on_attempt(
                    attempt_number,
                    "started",
                    None,
                )

            result = operation()

            if on_attempt:
                on_attempt(
                    attempt_number,
                    "success",
                    None,
                )

            return result

        except AgentError as error:
            last_error = error

            if on_attempt:
                on_attempt(
                    attempt_number,
                    "failed",
                    str(error),
                )

            if not error.retryable:
                raise

            if attempt_number >= total_attempts:
                raise

            delay = base_delay * (2 ** (attempt_number - 1))

            if jitter:
                delay += random.uniform(0, 0.5)

            if on_attempt:
                on_attempt(
                    attempt_number,
                    "retrying",
                    f"Retrying after {delay:.2f} seconds",
                )

            time.sleep(delay)

    raise last_error