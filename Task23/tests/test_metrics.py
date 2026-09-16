from app.evals.metrics import aggregate

def test_usage_aggregation():
    result = aggregate([
        {"latency_ms": 100, "total_tokens": 10, "scores": {"relevance":1,"groundedness":1,"correctness":1}},
        {"latency_ms": 200, "total_tokens": 20, "scores": {"relevance":0,"groundedness":1,"correctness":0}},
    ])
    assert result["total_tokens"] == 30
    assert result["average_latency_ms"] == 150
