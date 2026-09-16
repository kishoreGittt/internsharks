import json
import time
from pathlib import Path
from app.config import settings, MODEL_PRICING
from app.evals.deterministic import deterministic_scores
from app.evals.metrics import aggregate
from app.prompts.qa_v1 import SYSTEM_PROMPT as PROMPT_V1
from app.prompts.qa_v2 import SYSTEM_PROMPT as PROMPT_V2
from app.services.ai_service import AIService
from app.evals.judge import judge_answer

def load_suite(suite: str) -> list[dict]:
    path = Path(settings.dataset_dir) / f"{suite}.json"
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {suite}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ValueError("Evaluation dataset must be a non-empty JSON list")
    for item in data:
        for field in ["id", "question", "context", "should_refuse"]:
            if field not in item:
                raise ValueError(f"Invalid dataset case: missing {field}")
    return data

def calculate_cost(model: str, prompt_tokens, completion_tokens):
    if prompt_tokens is None or completion_tokens is None:
        return None
    pricing = MODEL_PRICING.get(model)
    if not pricing:
        return None
    return (prompt_tokens / 1_000_000) * pricing["input_cost_per_million_tokens"] + (completion_tokens / 1_000_000) * pricing["output_cost_per_million_tokens"]

def run_suite(suite: str, prompt_version: str, model: str | None = None, use_judge: bool = False) -> dict:
    cases = load_suite(suite)
    prompts = {"v1": PROMPT_V1, "v2": PROMPT_V2}
    if prompt_version not in prompts:
        raise ValueError(f"Invalid prompt version: {prompt_version}")
    service = AIService(model)
    results = []
    for case in cases:
        started = time.perf_counter()
        error = None
        try:
            output = service.answer(case["question"], case["context"], prompts[prompt_version])
            answer = output["answer"]
            checks = deterministic_scores(case, answer)
            scores = {
                "keyword_match": float(checks["keyword_match"]),
                "groundedness": 1.0 if checks["no_invented_database"] else 0.0,
                "relevance": 1.0 if checks["non_empty"] else 0.0,
                "correctness": float(checks["keyword_match"]),
            }
            if use_judge:
                judged = judge_answer(case["question"], case["context"], case.get("expected_answer"), answer, model)
                scores.update({k: judged[k] for k in ["relevance", "groundedness", "correctness"]})
            passed = all(checks.values()) and scores["relevance"] >= settings.min_relevance_score and scores["groundedness"] >= settings.min_groundedness_score and scores["correctness"] >= settings.min_correctness_score
            result = {
                "case_id": case["id"], "question": case["question"], "actual_answer": answer,
                "passed": passed, "scores": scores, "checks": checks,
                "latency_ms": round((time.perf_counter() - started) * 1000, 2),
                "prompt_tokens": output.get("prompt_tokens"), "completion_tokens": output.get("completion_tokens"),
                "total_tokens": output.get("total_tokens"),
                "estimated_cost_usd": calculate_cost(service.model, output.get("prompt_tokens"), output.get("completion_tokens")),
                "error": None,
            }
        except Exception as exc:
            result = {
                "case_id": case["id"], "question": case["question"], "actual_answer": "",
                "passed": False, "scores": {"keyword_match": 0, "groundedness": 0, "relevance": 0, "correctness": 0},
                "checks": {}, "latency_ms": round((time.perf_counter() - started) * 1000, 2),
                "prompt_tokens": None, "completion_tokens": None, "total_tokens": None,
                "estimated_cost_usd": None, "error": str(exc),
            }
        results.append(result)
    passed = sum(1 for r in results if r["passed"])
    summary = aggregate(results)
    return {
        "model": service.model, "prompt_version": prompt_version, "suite": suite,
        "total_cases": len(results), "passed": passed, "failed": len(results) - passed,
        "pass_rate": round((passed / len(results)) * 100, 2), **summary, "cases": results
    }
