from fastapi import APIRouter, HTTPException

from app.agent.runner import AgentRunner

from app.models.agent import (
    AgentRunRequest,
    AgentRunResponse,
    ExecutionTraceResponse
)

from app.storage.run_store import runs


router = APIRouter(
    prefix="/agent",
    tags=["AI Agent"]
)


agent_runner = AgentRunner()


@router.post(
    "/run",
    response_model=AgentRunResponse
)
def run_agent(
    request: AgentRunRequest
):

    goal = request.goal.strip()

    if not goal:
        raise HTTPException(
            status_code=400,
            detail="Goal cannot be empty."
        )

    try:

        result = agent_runner.run(
            goal
        )

        return {
            "success": True,
            "status_code": 200,
            "data": result
        }

    except RuntimeError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc)
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Agent execution failed."
        )


@router.get(
    "/runs/{run_id}",
    response_model=ExecutionTraceResponse
)
def get_agent_run(
    run_id: str
):

    run = runs.get(run_id)

    if not run:

        raise HTTPException(
            status_code=404,
            detail="Agent run not found."
        )

    return {
        "success": True,
        "status_code": 200,
        "data": run
    }