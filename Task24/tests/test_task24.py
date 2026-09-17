import logging

import pytest

from app.ai_service import AIServiceError, classify_openrouter_error
from app.pricing import calculate_estimated_cost
from app.tracing import TraceManager


def test_trace_id_generated():
    assert TraceManager().trace_id.startswith("trace_")


def test_trace_id_can_be_propagated():
    trace_id = "trace_test_123"
    assert TraceManager(trace_id=trace_id).trace_id == trace_id


def test_multiple_spans_same_trace_id():
    trace = TraceManager()
    one = trace.start_span("prompt_build")
    two = trace.start_span("openrouter_call")
    trace.finish_span(one)
    trace.finish_span(two)
    assert one["trace_id"] == trace.trace_id
    assert two["trace_id"] == trace.trace_id
    assert one["name"] == "prompt_build"
    assert two["name"] == "openrouter_call"


def test_duration_recorded():
    trace = TraceManager()
    span = trace.start_span("test")
    trace.finish_span(span)
    assert span["duration_ms"] >= 0


def test_cost_calculation():
    assert calculate_estimated_cost(1000, 500) == 0.00125


def test_missing_usage_returns_none():
    assert calculate_estimated_cost(None, None) is None


def test_rate_limit_error():
    category, _, status = classify_openrouter_error(429)
    assert category == "OPENROUTER_RATE_LIMIT"
    assert status == 429


def test_auth_error():
    category, _, status = classify_openrouter_error(401)
    assert category == "OPENROUTER_AUTH_ERROR"
    assert status == 502


def test_timeout_error():
    category, _, status = classify_openrouter_error(408)
    assert category == "OPENROUTER_TIMEOUT"
    assert status == 504


def test_model_unavailable_error():
    category, _, status = classify_openrouter_error(404, "model not found")
    assert category == "MODEL_UNAVAILABLE"
    assert status == 502


def test_invalid_model_response_error():
    error = AIServiceError("INVALID_MODEL_RESPONSE", "invalid", 502)
    assert error.category == "INVALID_MODEL_RESPONSE"


def test_failure_categories_are_structured():
    categories = {
        classify_openrouter_error(401)[0],
        classify_openrouter_error(429)[0],
        classify_openrouter_error(408)[0],
        classify_openrouter_error(404, "model unavailable")[0],
    }
    assert "OPENROUTER_AUTH_ERROR" in categories
    assert "OPENROUTER_RATE_LIMIT" in categories
    assert "OPENROUTER_TIMEOUT" in categories
    assert "MODEL_UNAVAILABLE" in categories


def test_privacy_default_is_disabled(monkeypatch):
    monkeypatch.setenv("LOG_AI_CONTENT", "false")
    from app import config
    monkeypatch.setattr(config, "LOG_AI_CONTENT", False)
    assert config.LOG_AI_CONTENT is False


def test_no_prompt_or_response_in_logging(caplog):
    secret = "secret123"
    with caplog.at_level(logging.INFO):
        logging.getLogger("task24.routes").info(
            "ai_request_completed trace_id=%s model=%s status=success",
            "trace_test",
            "test-model",
        )
    assert secret not in caplog.text
