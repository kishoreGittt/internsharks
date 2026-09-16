from app.models.judge import JudgeResponse
from app.services.ai_service import AIService
from app.prompts.judge_prompt import JUDGE_SYSTEM_PROMPT

def judge_answer(question: str, context: str, expected: str | None, actual: str, model: str | None = None) -> dict:
    # Optional judge implementation. It uses the same provider service.
    service = AIService(model)
    prompt = (
        f"Question: {question}\nContext: {context}\nExpected: {expected}\n"
        f"Actual: {actual}\nReturn JSON only."
    )
    result = service.answer(prompt, context, JUDGE_SYSTEM_PROMPT)
    parsed = JudgeResponse.model_validate_json(result["answer"])
    return parsed.model_dump()
