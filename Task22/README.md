# Task 22 - Resilient AI Agent

## Features
- FastAPI Project Operations Agent
- MongoDB persistence
- Retry with exponential backoff
- Retryable/non-retryable errors
- Timeout handling
- Idempotency records
- Run details and resume endpoint
- Deterministic unreliable external tool
- Pytest tests

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Start MongoDB, then run:

```powershell
uvicorn app.main:app --reload
```

## Endpoints

### Start run
POST `/agent/runs`

```json
{
  "goal": "Create Project Nova",
  "failure_mode": "temporary_failure"
}
```

Allowed failure modes:
- success
- temporary_failure
- timeout
- permanent_failure

### Get run
GET `/agent/runs/{run_id}`

### Resume
POST `/agent/runs/{run_id}/resume`

## Tests

```powershell
pytest -q
```

## Reliability behavior

Temporary failures are retried up to `MAX_RETRIES`. Delays use exponential backoff:

`delay = RETRY_BASE_DELAY * 2^(attempt - 1)`

Non-retryable errors run only once. Write actions use an idempotency key:

`run_id:action_id`

The same executed action returns its stored result instead of creating another side effect.

## Do not commit

- `.env`
- API keys
- `.venv`
- `__pycache__`
- logs
