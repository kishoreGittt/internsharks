from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from app.reliability.errors import ToolTimeoutError

def run_with_timeout(operation, timeout_seconds):
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(operation)
        try:
            return future.result(timeout=timeout_seconds)
        except FutureTimeout:
            future.cancel()
            raise ToolTimeoutError()
