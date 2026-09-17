from typing import Optional
from app.config import MODEL_INPUT_PRICE_PER_MILLION, MODEL_OUTPUT_PRICE_PER_MILLION

def calculate_estimated_cost(
    prompt_tokens: Optional[int],
    completion_tokens: Optional[int],
) -> Optional[float]:
    if prompt_tokens is None or completion_tokens is None:
        return None

    input_cost = prompt_tokens / 1_000_000 * MODEL_INPUT_PRICE_PER_MILLION
    output_cost = completion_tokens / 1_000_000 * MODEL_OUTPUT_PRICE_PER_MILLION
    return round(input_cost + output_cost, 8)
