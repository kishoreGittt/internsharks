"""
Task24 AI Observability API routes.
"""

import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.ai_service import (
    AIServiceError,
    generate_ai_response,
)
from app.database import get_database
from app.pricing import calculate_estimated_cost


router = APIRouter()


class AIRequest(BaseModel):
    """
    Request body for the AI endpoint.
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=10_000,
    )

    prompt_version: str = Field(
        default="v1",
        min_length=1,
        max_length=50,
    )


def create_trace_id() -> str:
    """
    Create a unique trace ID.
    """

    return f"trace_{uuid.uuid4().hex}"


def utc_now() -> datetime:
    """
    Return current UTC time.
    """

    return datetime.now(timezone.utc)


async def save_trace(trace_data: Dict[str, Any]) -> None:
    """
    Save a trace in MongoDB.
    """

    database = get_database()

    await database.traces.update_one(
        {
            "trace_id": trace_data["trace_id"],
        },
        {
            "$set": trace_data,
        },
        upsert=True,
    )


@router.get("/")
async def root() -> Dict[str, Any]:
    """
    Root endpoint.
    """

    return {
        "success": True,
        "status_code": 200,
        "message": "Task24 AI Observability API is running.",
    }


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Check API and MongoDB health.
    """

    try:
        database = get_database()

        await database.command("ping")

        return {
            "success": True,
            "status_code": 200,
            "data": {
                "api": "healthy",
                "database": "connected",
            },
        }

    except Exception as exc:
        return {
            "success": False,
            "status_code": 503,
            "data": {
                "api": "healthy",
                "database": "disconnected",
                "error": str(exc),
            },
        }


@router.post("/ai/ask")
async def ask_ai(
    request: AIRequest,
) -> Dict[str, Any]:
    """
    Send a request to OpenRouter and store the trace.
    """

    trace_id = create_trace_id()

    start_time = time.perf_counter()

    initial_trace = {
        "trace_id": trace_id,
        "prompt_version": request.prompt_version,
        "message": request.message,
        "status": "started",
        "started_at": utc_now(),
        "completed_at": None,
        "model": None,
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        },
        "estimated_cost": 0.0,
        "duration_ms": 0.0,
        "error": None,
    }

    try:
        await save_trace(initial_trace)

    except Exception as exc:
        print(f"Trace start logging failed: {exc}")

    try:
        result = generate_ai_response(
            message=request.message,
        )

        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        usage = result.get("usage", {}) or {}

        prompt_tokens = int(
            usage.get("prompt_tokens", 0) or 0
        )

        completion_tokens = int(
            usage.get("completion_tokens", 0) or 0
        )

        total_tokens = int(
            usage.get(
                "total_tokens",
                prompt_tokens + completion_tokens,
            )
            or 0
        )

        final_usage = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        }

        estimated_cost = calculate_estimated_cost(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

        successful_trace = {
            "trace_id": trace_id,
            "prompt_version": request.prompt_version,
            "message": request.message,
            "status": "success",
            "started_at": initial_trace["started_at"],
            "completed_at": utc_now(),
            "model": result.get("model"),
            "usage": final_usage,
            "estimated_cost": estimated_cost,
            "duration_ms": duration_ms,
            "error": None,
        }

        try:
            await save_trace(successful_trace)

        except Exception as exc:
            print(f"Successful trace logging failed: {exc}")

        return {
            "success": True,
            "status_code": 200,
            "data": {
                "trace_id": trace_id,
                "response": result.get("response", ""),
                "usage": final_usage,
                "estimated_cost": estimated_cost,
            },
        }

    except AIServiceError as exc:
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        failed_trace = {
            "trace_id": trace_id,
            "prompt_version": request.prompt_version,
            "message": request.message,
            "status": "failed",
            "started_at": initial_trace["started_at"],
            "completed_at": utc_now(),
            "model": None,
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
            "estimated_cost": 0.0,
            "duration_ms": duration_ms,
            "error": str(exc),
        }

        try:
            await save_trace(failed_trace)

        except Exception as logging_exc:
            print(
                f"Failed trace logging failed: {logging_exc}"
            )

        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "status_code": 502,
                "error": "AI_SERVICE_ERROR",
                "message": str(exc),
                "trace_id": trace_id,
            },
        )

    except Exception as exc:
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        failed_trace = {
            "trace_id": trace_id,
            "prompt_version": request.prompt_version,
            "message": request.message,
            "status": "failed",
            "started_at": initial_trace["started_at"],
            "completed_at": utc_now(),
            "model": None,
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
            "estimated_cost": 0.0,
            "duration_ms": duration_ms,
            "error": str(exc),
        }

        try:
            await save_trace(failed_trace)

        except Exception as logging_exc:
            print(
                f"Unexpected error logging failed: "
                f"{logging_exc}"
            )

        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "status_code": 500,
                "error": "INTERNAL_SERVER_ERROR",
                "message": str(exc),
                "trace_id": trace_id,
            },
        )


# IMPORTANT:
# These fixed routes must be declared BEFORE
# /observability/traces/{trace_id}.


@router.get("/observability/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    Return observability metrics.
    """

    try:
        database = get_database()

        total_traces = await database.traces.count_documents({})

        successful_traces = await database.traces.count_documents(
            {
                "status": "success",
            }
        )

        failed_traces = await database.traces.count_documents(
            {
                "status": "failed",
            }
        )

        duration_pipeline = [
            {
                "$match": {
                    "duration_ms": {
                        "$exists": True,
                        "$ne": None,
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "average_duration_ms": {
                        "$avg": "$duration_ms",
                    },
                }
            },
        ]

        duration_result = await database.traces.aggregate(
            duration_pipeline
        ).to_list(length=1)

        average_duration_ms = 0.0

        if duration_result:
            average_duration_ms = round(
                duration_result[0].get(
                    "average_duration_ms",
                    0,
                )
                or 0,
                2,
            )

        cost_pipeline = [
            {
                "$match": {
                    "estimated_cost": {
                        "$exists": True,
                        "$ne": None,
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_estimated_cost": {
                        "$sum": "$estimated_cost",
                    },
                }
            },
        ]

        cost_result = await database.traces.aggregate(
            cost_pipeline
        ).to_list(length=1)

        total_estimated_cost = 0.0

        if cost_result:
            total_estimated_cost = round(
                cost_result[0].get(
                    "total_estimated_cost",
                    0,
                )
                or 0,
                8,
            )

        success_rate_percent = 0.0

        if total_traces > 0:
            success_rate_percent = round(
                (successful_traces / total_traces) * 100,
                2,
            )

        return {
            "success": True,
            "status_code": 200,
            "data": {
                "total_traces": total_traces,
                "successful_traces": successful_traces,
                "failed_traces": failed_traces,
                "success_rate_percent": success_rate_percent,
                "average_duration_ms": average_duration_ms,
                "total_estimated_cost": total_estimated_cost,
            },
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "status_code": 500,
                "error": "METRICS_ERROR",
                "message": str(exc),
            },
        )


@router.get("/observability/traces/slow")
async def get_slow_traces(
    threshold_ms: float = Query(
        default=1000,
        ge=0,
        description="Minimum trace duration in milliseconds.",
    ),
) -> Dict[str, Any]:
    """
    Return slow traces.
    """

    try:
        database = get_database()

        traces = await database.traces.find(
            {
                "duration_ms": {
                    "$gte": threshold_ms,
                }
            },
            {
                "_id": 0,
            },
        ).sort(
            "duration_ms",
            -1,
        ).to_list(length=100)

        return {
            "success": True,
            "status_code": 200,
            "data": {
                "threshold_ms": threshold_ms,
                "count": len(traces),
                "traces": traces,
            },
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "status_code": 500,
                "error": "SLOW_TRACES_ERROR",
                "message": str(exc),
            },
        )


@router.get("/observability/traces/failures")
async def get_failed_traces() -> Dict[str, Any]:
    """
    Return failed traces.
    """

    try:
        database = get_database()

        traces = await database.traces.find(
            {
                "status": "failed",
            },
            {
                "_id": 0,
            },
        ).sort(
            "started_at",
            -1,
        ).to_list(length=100)

        return {
            "success": True,
            "status_code": 200,
            "data": {
                "count": len(traces),
                "traces": traces,
            },
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "status_code": 500,
                "error": "FAILURES_ERROR",
                "message": str(exc),
            },
        )


@router.get("/observability/traces/{trace_id}")
async def get_trace(
    trace_id: str,
) -> Dict[str, Any]:
    """
    Get one trace by trace ID.
    """

    try:
        database = get_database()

        trace = await database.traces.find_one(
            {
                "trace_id": trace_id,
            },
            {
                "_id": 0,
            },
        )

        if not trace:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "status_code": 404,
                    "error": "TRACE_NOT_FOUND",
                    "message": "Trace was not found.",
                },
            )

        return {
            "success": True,
            "status_code": 200,
            "data": trace,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "status_code": 500,
                "error": "TRACE_LOOKUP_ERROR",
                "message": str(exc),
            },
        )