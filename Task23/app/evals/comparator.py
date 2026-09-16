def compare_case_results(baseline: list[dict], candidate: list[dict]) -> dict:
    b = {x["case_id"]: x for x in baseline}
    c = {x["case_id"]: x for x in candidate}
    regressions, improvements, still_passing, still_failing = [], [], [], []
    for case_id in sorted(set(b) | set(c)):
        bp, cp = b.get(case_id, {}).get("passed", False), c.get(case_id, {}).get("passed", False)
        if bp and not cp: regressions.append(case_id)
        elif not bp and cp: improvements.append(case_id)
        elif bp and cp: still_passing.append(case_id)
        else: still_failing.append(case_id)
    return {
        "regressions": regressions,
        "improvements": improvements,
        "still_passing": still_passing,
        "still_failing": still_failing,
    }
