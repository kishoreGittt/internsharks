import pytest
from app.reliability.retry import retry_call
from app.reliability.errors import RetryableError, NonRetryableError

def test_temporary_failure_then_success():
    state = {"attempts": 0}
    def operation(attempt):
        state["attempts"] += 1
        if state["attempts"] < 3:
            raise RetryableError("temporary")
        return "success"

    assert retry_call(operation, max_retries=3, base_delay=0) == "success"
    assert state["attempts"] == 3

def test_retry_exhaustion():
    state = {"attempts": 0}
    def operation(attempt):
        state["attempts"] += 1
        raise RetryableError("temporary")

    with pytest.raises(RetryableError):
        retry_call(operation, max_retries=3, base_delay=0)
    assert state["attempts"] == 3

def test_non_retryable_error_runs_once():
    state = {"attempts": 0}
    def operation(attempt):
        state["attempts"] += 1
        raise NonRetryableError("invalid")

    with pytest.raises(NonRetryableError):
        retry_call(operation, max_retries=3, base_delay=0)
    assert state["attempts"] == 1
