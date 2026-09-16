from typing import Any
from pydantic import BaseModel, Field

class EvalRunRequest(BaseModel):
    suite: str = "rag_basic"
    prompt_version: str = "v2"
    model: str | None = None
    use_judge: bool | None = None

class CompareRequest(BaseModel):
    suite: str = "rag_basic"
    baseline_prompt: str = "v1"
    candidate_prompt: str = "v2"
    model: str | None = None
    use_judge: bool | None = None

class StructuredAnswer(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1)

class JudgeScore(BaseModel):
    relevance: float = Field(ge=0, le=1)
    groundedness: float = Field(ge=0, le=1)
    correctness: float = Field(ge=0, le=1)
    reason: str = ""

class CaseResult(BaseModel):
    case_id: str
    question: str
    actual_answer: str
    passed: bool
    scores: dict[str, float]
    latency_ms: float
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    estimated_cost_usd: float | None = None
    checks: dict[str, Any] = {}
    error: str | None = None
