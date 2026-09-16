import json
import re
from typing import Any
from app.models.evaluation import StructuredAnswer

REFUSAL_PHRASES = [
    "not available",
    "not provided",
    "information is unavailable",
    "cannot determine",
    "does not mention",
    "no information",
]

def keyword_match(answer: str, keywords: list[str]) -> float:
    if not keywords:
        return 1.0
    lower = answer.lower()
    return sum(k.lower() in lower for k in keywords) / len(keywords)

def refusal_check(answer: str, should_refuse: bool) -> bool:
    if not should_refuse:
        return True
    lower = answer.lower()
    return any(phrase in lower for phrase in REFUSAL_PHRASES)

def non_empty_check(answer: str) -> bool:
    return bool(answer and answer.strip())

def structured_check(answer: str) -> tuple[bool, str]:
    try:
        data: Any = json.loads(answer)
        StructuredAnswer.model_validate(data)
        return True, ""
    except Exception as exc:
        return False, str(exc)

def forbidden_database_check(answer: str, should_refuse: bool) -> bool:
    if not should_refuse:
        return True
    forbidden = ["postgresql", "mysql", "mongodb", "sqlite", "oracle"]
    lower = answer.lower()
    return not any(word in lower for word in forbidden)

def deterministic_scores(case: dict, answer: str) -> dict:
    checks = {
        "non_empty": non_empty_check(answer),
        "keyword_match": keyword_match(answer, case.get("expected_keywords", [])),
        "refusal": refusal_check(answer, case.get("should_refuse", False)),
        "no_invented_database": forbidden_database_check(answer, case.get("should_refuse", False)),
    }
    if case.get("structured"):
        checks["structured_output"] = structured_check(answer)[0]
    return checks
