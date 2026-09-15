from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.agent.runner import create_run, run_agent
from app.storage.database import runs_collection
from app.reliability.errors import AgentError

router = APIRouter(prefix="/agent", tags=["Agent"])

class RunRequest(BaseModel):
    goal: str = Field(min_length=1)
    failure_mode: str = "success"

@router.post("/runs")
def start_run(request: RunRequest):
    run_id = create_run(request.goal)
    try:
        result = run_agent(run_id, request.goal, request.failure_mode)
        return {"success": True, "status_code": 200, "data": result}
    except AgentError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={
                "success": False,
                "status_code": exc.status_code,
                "error": exc.code,
                "message": exc.message,
                "run_id": run_id
            }
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail={
            "success": False, "status_code": 500,
            "error": "AGENT_ERROR", "message": str(exc), "run_id": run_id
        })

@router.get("/runs/{run_id}")
def get_run(run_id: str):
    run = runs_collection.find_one({"run_id": run_id}, {"_id": 0})
    if not run:
        raise HTTPException(status_code=404, detail={
            "success": False, "status_code": 404,
            "error": "RUN_NOT_FOUND", "message": "Run not found"
        })
    return {"success": True, "status_code": 200, "data": run}

@router.post("/runs/{run_id}/resume")
def resume_run(run_id: str):
    run = runs_collection.find_one({"run_id": run_id}, {"_id": 0})
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    if run["status"] == "completed":
        raise HTTPException(status_code=409, detail={
            "success": False, "status_code": 409,
            "error": "RUN_NOT_RESUMABLE", "message": "Completed run cannot resume"
        })
    try:
        result = run_agent(run_id, run["goal"], "success")
        return {"success": True, "status_code": 200, "data": result}
    except AgentError as exc:
        raise HTTPException(status_code=exc.status_code, detail={
            "success": False, "status_code": exc.status_code,
            "error": exc.code, "message": exc.message
        })
