# Task 23: LLM Evaluation & Prompt Regression Testing

A beginner-friendly FastAPI evaluation system for testing AI/RAG answers.

## Features

- 15 evaluation cases
- Deterministic keyword, refusal, non-empty, forbidden-fact and structured JSON checks
- Optional OpenRouter LLM-as-a-judge
- Configurable score thresholds
- Prompt versions `v1` and `v2`
- Baseline vs candidate regression comparison
- Latency, token usage and approximate cost tracking
- SQLite persistence
- Pytest tests
- Mock mode when `OPENROUTER_API_KEY` is not configured

## Setup in PowerShell

```powershell
cd D:\INTERNSHARK-TASKS\Task23
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Open Swagger:
`http://127.0.0.1:8000/docs`

## Run evaluation

POST `/eval/run`

```json
{
  "suite": "rag_basic",
  "prompt_version": "v2"
}
```

## Compare prompts

POST `/eval/compare`

```json
{
  "suite": "rag_basic",
  "baseline_prompt": "v1",
  "candidate_prompt": "v2"
}
```

## Get report

GET `/eval/runs/{run_id}`

## Get failures

GET `/eval/runs/{run_id}/failures`

## Run tests

```powershell
pytest -q
```

## OpenRouter mode

Put your key in `.env`:

```env
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=your_available_model
```

Never commit `.env` or API keys.

## Important limitation

If the provider does not return token usage, the project stores `null` for token fields and cannot calculate a reliable cost. The included mock mode is for local learning and testing; it is not a real LLM.
