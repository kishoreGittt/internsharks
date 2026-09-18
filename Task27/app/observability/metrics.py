def approximate_cost(
    input_tokens: int,
    output_tokens: int
):

    # Approximation only.
    # Update these values according to
    # the model/provider pricing.

    input_cost_per_million = 0.0

    output_cost_per_million = 0.0

    cost = (

        (
            input_tokens
            / 1_000_000
        )
        * input_cost_per_million

        +

        (
            output_tokens
            / 1_000_000
        )
        * output_cost_per_million
    )

    return round(
        cost,
        8
    )