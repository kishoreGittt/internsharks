from app.evals.comparator import compare_case_results

def test_regression_detection():
    result = compare_case_results(
        [{"case_id":"eval_001","passed":True}],
        [{"case_id":"eval_001","passed":False}],
    )
    assert result["regressions"] == ["eval_001"]

def test_improvement_detection():
    result = compare_case_results(
        [{"case_id":"eval_002","passed":False}],
        [{"case_id":"eval_002","passed":True}],
    )
    assert result["improvements"] == ["eval_002"]
