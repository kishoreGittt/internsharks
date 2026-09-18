import pytest

from app.evals.runner import (
    run_evaluation
)


@pytest.mark.asyncio
async def test_evaluation():

    result = await run_evaluation()

    assert result[
        "total_cases"
    ] >= 10

    assert "passed" in result

    assert "failed" in result