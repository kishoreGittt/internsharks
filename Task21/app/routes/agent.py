from fastapi import APIRouter, HTTPException

from app.models.agent import (
    AgentRunCreate,
    ApprovalRequest
)

from app.agent.runner import (
    create_agent_run
)

from app.storage.run_repository import (
    get_run
)

from app.services.approval_service import (
    process_approval
)


router = APIRouter(
    prefix="/agent",
    tags=["Agent"]
)


@router.post("/runs")
async def create_run(
    request: AgentRunCreate
):

    try:

        result = await create_agent_run(
            request.goal
        )

        return {
            "success": True,
            "status_code": 200,
            "data": result
        }

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Unable to create agent run"
        )


@router.get("/runs/{run_id}")
async def get_agent_run(
    run_id: str
):

    run = await get_run(run_id)

    if not run:

        raise HTTPException(
            status_code=404,
            detail="Agent run not found"
        )

    return {
        "success": True,
        "status_code": 200,
        "data": {
            "run_id": run["run_id"],
            "goal": run["goal"],
            "status": run["status"],
            "step_count": run["step_count"],
            "pending_action": run.get(
                "pending_action"
            )
        }
    }


@router.post(
    "/runs/{run_id}/actions/{action_id}/approval"
)
async def approve_action(
    run_id: str,
    action_id: str,
    request: ApprovalRequest
):

    try:

        result = await process_approval(
            run_id,
            action_id,
            request.approved
        )

        return {
            "success": True,
            "status_code": 200,
            "data": result
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Approval processing failed"
        )