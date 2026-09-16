from app.ai_service import classify_openrouter_error
from app.pricing import calculate_estimated_cost
from app.tracing import TraceManager

def test_trace_id_generated():
    assert TraceManager().trace_id.startswith("trace_")

def test_multiple_spans_same_trace_id():
    trace = TraceManager()
    one = trace.start_span("prompt_build")
    two = trace.start_span("openrouter_call")
    trace.finish_span(one)
    trace.finish_span(two)
    assert one["trace_id"] == trace.trace_id
    assert two["trace_id"] == trace.trace_id

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
