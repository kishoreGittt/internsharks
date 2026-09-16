from app.evals.deterministic import keyword_match, refusal_check, structured_check

def test_keyword_match_pass():
    assert keyword_match("Arun manages Nova", ["Arun"]) == 1.0

def test_keyword_match_fail():
    assert keyword_match("Ravi manages Nova", ["Arun"]) == 0.0

def test_refusal_pass():
    assert refusal_check("Information is not available.", True)

def test_refusal_fail():
    assert not refusal_check("The salary is 50000.", True)

def test_valid_structured_response():
    assert structured_check('{"answer":"Arun","confidence":0.9}')[0]

def test_invalid_structured_response():
    assert not structured_check('{"answer":"Arun"}')[0]
