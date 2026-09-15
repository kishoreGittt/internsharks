from datetime import datetime, timezone
from uuid import uuid4
from app.storage.database import runs_collection
from app.tools.external_tools import resilient_external_status
from app.reliability.idempotency import execute_idempotently
from app.services.project_service import create_project, add_employee, create_task
from app.reliability.errors import AgentError

def now():
    return datetime.now(timezone.utc)

def create_run(goal):
    run_id = f"run_{uuid4().hex[:12]}"
    runs_collection.insert_one({
        "run_id": run_id,
        "goal": goal,
        "status": "running",
        "step_count": 0,
        "trace": [],
        "created_at": now(),
        "updated_at": now()
    })
    return run_id

def update_run(run_id, values):
    values["updated_at"] = now()
    runs_collection.update_one({"run_id": run_id}, {"$set": values})

def run_agent(run_id, goal, failure_mode="success"):
    trace = []
    try:
        action1 = f"{run_id}:create_project"
        project, cached = execute_idempotently(
            run_id, "create_project", "create_project",
            lambda: create_project("Nova")
        )
        trace.append({"step": 1, "tool": "create_project",
                      "status": "cached" if cached else "success"})

        action2 = f"{run_id}:external_status"
        status = resilient_external_status("Nova", failure_mode, trace)
        trace.append({"step": 2, "tool": "get_external_project_status",
                      "status": "success"})

        update_run(run_id, {
            "status": "completed",
            "step_count": 2,
            "trace": trace,
            "result": {"project": project, "external_status": status}
        })
        return {"run_id": run_id, "status": "completed", "trace": trace}

    except AgentError as exc:
        final_status = "partially_completed" if trace else "failed"
        update_run(run_id, {
            "status": final_status,
            "step_count": len(trace),
            "trace": trace,
            "error": {"code": exc.code, "message": exc.message}
        })
        raise
    except Exception as exc:
        update_run(run_id, {
            "status": "failed",
            "trace": trace,
            "error": {"code": "UNEXPECTED_ERROR", "message": str(exc)}
        })
        raise
