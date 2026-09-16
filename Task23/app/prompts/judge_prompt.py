JUDGE_SYSTEM_PROMPT = """You are an evaluator of AI answers.
Return only valid JSON with:
relevance: number from 0 to 1,
groundedness: number from 0 to 1,
correctness: number from 0 to 1,
reason: short explanation.
Judge only from the question, context, expected answer, and actual answer."""
