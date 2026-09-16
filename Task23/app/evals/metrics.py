from statistics import mean

def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    index = (len(values) - 1) * p
    low, high = int(index), min(int(index) + 1, len(values) - 1)
    return values[low] + (values[high] - values[low]) * (index - low)

def aggregate(results: list[dict]) -> dict:
    latencies = [r["latency_ms"] for r in results]
    total_tokens = sum(r.get("total_tokens") or 0 for r in results)
    costs = [r.get("estimated_cost_usd") for r in results if r.get("estimated_cost_usd") is not None]
    return {
        "average_latency_ms": round(mean(latencies), 2) if latencies else 0,
        "minimum_latency_ms": round(min(latencies), 2) if latencies else 0,
        "maximum_latency_ms": round(max(latencies), 2) if latencies else 0,
        "p95_latency_ms": round(percentile(latencies, 0.95), 2) if latencies else None,
        "total_tokens": total_tokens,
        "estimated_cost_usd": round(sum(costs), 8) if costs else None,
        "average_relevance": round(mean(r["scores"].get("relevance", 0) for r in results), 3) if results else 0,
        "average_groundedness": round(mean(r["scores"].get("groundedness", 0) for r in results), 3) if results else 0,
        "average_correctness": round(mean(r["scores"].get("correctness", 0) for r in results), 3) if results else 0,
    }
