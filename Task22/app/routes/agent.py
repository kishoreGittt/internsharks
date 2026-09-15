from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.reliability.errors import AgentError
from app.services.project_service import ProjectService
from app.storage.database import database


router = APIRouter(
    prefix="/agent",
    tags=["Agent"],
)

project_service = ProjectService(database)


class RunRequest(BaseModel):
    project_id: str = Field(
        default="project-001",
        min_length=1,
    )

    failure_mode: str = Field(
        default="success",
        pattern="^(success|temporary_failure|timeout|permanent_failure)$",
    )

    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
    )


class IdempotentActionRequest(BaseModel):
    run_id: str = Field(min_length=1)
    action_id: str = Field(min_length=1)
    project_name: str = Field(min_length=1)


def error_response(
    error: AgentError,
    run_id: str | None = None,
):
    return {
        "success": False,
        "run_id": run_id,
        "error_code": error.code,
        "message": error.message,
    }


@router.post("/runs")
def create_run(payload: RunRequest):
    run_id = project_service.create_run(
        payload.model_dump()
    )

    try:
        result = project_service.execute_run(run_id)

        return {
            "success": True,
            "run_id": run_id,
            "status": "completed",
            "result": result,
        }

    except AgentError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error_response(error, run_id),
        )


@router.get("/runs/{run_id}")
def get_run(run_id: str):
    run = project_service.get_run(run_id)

    if not run:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error_code": "RUN_NOT_FOUND",
                "message": "Run not found",
            },
        )

    run["_id"] = str(run["_id"])

    for field in ("created_at", "updated_at"):
        if isinstance(run.get(field), datetime):
            run[field] = run[field].isoformat()

    return {
        "success": True,
        "data": run,
    }


@router.post("/runs/{run_id}/resume")
def resume_run(run_id: str):
    run = project_service.get_run(run_id)

    if not run:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error_code": "RUN_NOT_FOUND",
                "message": "Run not found",
            },
        )

    if run.get("status") == "completed":
        raise HTTPException(
            status_code=409,
            detail={
                "success": False,
                "error_code": "RUN_ALREADY_COMPLETED",
                "message": "Completed run cannot be resumed",
            },
        )

    try:
        result = project_service.execute_run(run_id)

        return {
            "success": True,
            "run_id": run_id,
            "status": "completed",
            "result": result,
        }

    except AgentError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error_response(error, run_id),
        )


@router.post("/actions/idempotent")
def idempotent_action(
    payload: IdempotentActionRequest,
):
    result = project_service.execute_idempotent_action(
        run_id=payload.run_id,
        action_id=payload.action_id,
        project_name=payload.project_name,
    )

    return {
        "success": True,
        "data": result,
    }