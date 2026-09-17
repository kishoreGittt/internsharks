# Task 24 - AI Observability with FastAPI, OpenRouter and MongoDB Atlas

Task 24 builds a small observability layer around an AI request. It tracks what happened during a request without storing private prompt/response content by default.

## What is implemented

- `POST /ai/ask`
- Request-level `trace_id` propagation through `RequestTrackingMiddleware`
- Span-level tracing stored in MongoDB (`prompt_build`, `openrouter_call`, and validation spans when applicable)
- `GET /observability/traces/{trace_id}` returns the trace plus its spans
- Token usage and estimated cost
- Prompt-version and exact model tracking
- Privacy-first telemetry: with `LOG_AI_CONTENT=false`, complete prompt/response text is not stored or logged
- Structured error categories including `OPENROUTER_TIMEOUT`, `OPENROUTER_RATE_LIMIT`, `OPENROUTER_AUTH_ERROR`, `MODEL_UNAVAILABLE`, `INVALID_MODEL_RESPONSE`, `TOOL_EXECUTION_ERROR`, `RETRIEVAL_ERROR`, `VALIDATION_ERROR`, and `INTERNAL_ERROR`
- p50 and p95 latency
- Metrics grouped by model and prompt version
- Failure filtering by `error_category`
- Pagination for failure and slow-trace APIs
- Pytest coverage for tracing, pricing, error classification and privacy defaults

## Setup

```powershell
cd D:\INTERNSHARK-TASKS\Task24
pip install -r requirements.txt
```

Create `.env` from `.env.example` and add your real MongoDB Atlas URI and OpenRouter API key.

Run:

```powershell
uvicorn app.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Main endpoints

### Ask AI

`POST /ai/ask`

```json
{
  "message": "Explain FastAPI in simple words.",
  "prompt_version": "assistant_v1"
}
```

The response includes `trace_id`, token usage when the provider supplies it, and estimated cost.

### Trace with spans

`GET /observability/traces/{trace_id}`

A successful trace contains spans similar to:

```json
"spans": [
  {"name": "prompt_build", "duration_ms": 0.1, "status": "success"},
  {"name": "openrouter_call", "duration_ms": 900, "status": "success"}
]
```

### Metrics

`GET /observability/metrics`

Returns totals, average latency, p50, p95, total tokens, estimated cost, statistics grouped by model and prompt version, and failure counts by category.

**p50** is the median latency: about half of requests are at or below it. **p95** is the latency at or below which about 95% of requests fall; it helps reveal slow-tail behavior that an average can hide.

### Slow traces

`GET /observability/traces/slow`

Optional query parameters:

```text
?threshold_ms=3000&page=1&page_size=20
```

### Failure traces

`GET /observability/traces/failures`

Optional filter and pagination:

```text
?error_category=OPENROUTER_TIMEOUT&page=1&page_size=20
```

## Privacy

`LOG_AI_CONTENT=false` is the default. The trace stores metadata such as prompt/response lengths, not the complete prompt or response. Application logs also contain operational metadata only.

Never commit `.env`, API keys, MongoDB passwords, `.venv`, `__pycache__`, secrets, or sensitive prompt content.

## MongoDB

Database: `task24_db` by default.

Collections:

- `traces`
- `spans`

## Tests

```powershell
pytest -v tests/
```

Tests mock/avoid external provider calls where appropriate.
