# Task 24 - AI Observability with FastAPI, OpenRouter and MongoDB Atlas

## Features

- POST `/ai/ask`
- Unique trace IDs
- Trace and span storage in MongoDB Atlas
- Token usage and estimated cost
- Prompt version and model tracking
- Failure categorization
- Metrics API
- Slow request API
- Failure filtering and pagination
- Privacy-first metadata logging
- Pytest tests

## Setup

```powershell
cd D:\INTERNSHARK-TASKS\Task24
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your MongoDB Atlas URI and OpenRouter API key.

Run:

```powershell
uvicorn app.main:app --reload
```

Open Swagger:

`http://127.0.0.1:8000/docs`

## Endpoints

- `GET /`
- `GET /health`
- `POST /ai/ask`
- `GET /observability/traces/{trace_id}`
- `GET /observability/metrics`
- `GET /observability/traces/slow`
- `GET /observability/traces/failures`
- `GET /observability/traces/failures?error_category=OPENROUTER_TIMEOUT`

## MongoDB collections

Database: `task24_db`

Collections:

- `traces`
- `spans`

## Privacy

`LOG_AI_CONTENT=false` is the default. The application stores prompt and response lengths, not complete prompt or response content.

Never commit:

- `.env`
- API keys
- MongoDB passwords
- `.venv`
- `__pycache__`

## Tests

```powershell
pytest -q
```

## Postman

### Ask AI

POST `http://127.0.0.1:8000/ai/ask`

Body:

```json
{
  "message": "Explain FastAPI in simple words."
}
```

Copy the returned `trace_id`.

### Get trace

GET `http://127.0.0.1:8000/observability/traces/<trace_id>`

### Metrics

GET `http://127.0.0.1:8000/observability/metrics`

### Slow traces

GET `http://127.0.0.1:8000/observability/traces/slow`

### Failures

GET `http://127.0.0.1:8000/observability/traces/failures`

## Important

Update model pricing in `.env` according to the actual model/provider pricing. If OpenRouter does not return token usage, token fields remain null.
