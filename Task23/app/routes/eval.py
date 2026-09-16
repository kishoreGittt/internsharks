from fastapi import APIRouter, HTTPException
from app.models.evaluation import EvalRunRequest, CompareRequest
from app.evals.runner import run_suite
from app.evals.comparator import compare_case_results
from app.storage.evaluation_repository import save_run, get_run

router = APIRouter(prefix="/eval", tags=["Evaluation"])

@router.post("/run")
def evaluate(request: EvalRunRequest):
    try:
        report = run_suite(request.suite, request.prompt_version, request.model, request.use_judge or False)
        run_id = save_run(report)
        return {"success": True, "status_code": 200, "data": {"run_id": run_id, **{k:v for k,v in report.items() if k != "cases"}}}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Evaluation failed: {exc}")

@router.post("/compare")
def compare(request: CompareRequest):
    try:
        baseline = run_suite(request.suite, request.baseline_prompt, request.model, request.use_judge or False)
        candidate = run_suite(request.suite, request.candidate_prompt, request.model, request.use_judge or False)
        categories = compare_case_results(baseline["cases"], candidate["cases"])
        return {
            "success": True, "status_code": 200,
            "data": {
                "baseline": {k: baseline[k] for k in ["prompt_version", "pass_rate", "passed", "failed"]},
                "candidate": {k: candidate[k] for k in ["prompt_version", "pass_rate", "passed", "failed"]},
                "change": round(candidate["pass_rate"] - baseline["pass_rate"], 2),
                **categories
            }
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.get("/runs/{run_id}")
def run_details(run_id: str):
    report = get_run(run_id)
    if not report:
        raise HTTPException(status_code=404, detail="Evaluation run not found")
    return {"success": True, "status_code": 200, "data": report}

@router.get("/runs/{run_id}/failures")
def failures(run_id: str):
    report = get_run(run_id)
    if not report:
        raise HTTPException(status_code=404, detail="Evaluation run not found")
    return {"success": True, "status_code": 200, "data": [c for c in report["cases"] if not c["passed"]]}
