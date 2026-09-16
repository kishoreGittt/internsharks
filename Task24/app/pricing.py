"""
Token pricing and estimated cost calculation.

The prices below are example prices per 1 million tokens.
Update them according to the model/provider pricing you use.
"""

INPUT_PRICE_PER_MILLION = 0.50
OUTPUT_PRICE_PER_MILLION = 1.50


def calculate_estimated_cost(
    prompt_tokens: int,
    completion_tokens: int,
) -> float:
    """
    Calculate estimated AI request cost.

    Args:
        prompt_tokens: Number of input tokens.
        completion_tokens: Number of output tokens.

    Returns:
        Estimated cost in USD.
    """

    prompt_tokens = prompt_tokens or 0
    completion_tokens = completion_tokens or 0

    input_cost = (
        prompt_tokens / 1_000_000
    ) * INPUT_PRICE_PER_MILLION

    output_cost = (
        completion_tokens / 1_000_000
    ) * OUTPUT_PRICE_PER_MILLION

    total_cost = input_cost + output_cost

    return round(total_cost, 8)