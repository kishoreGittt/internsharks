import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request

from app.ai_service import AIServiceError, call_openrouter
from app.config import (
    LOG_AI_CONTENT,
    OPENROUTER_MODEL,
    PROMPT_VERSION,
    SLOW_REQUEST_THRESHOLD_MS,
)
from app.database import (
    get_spans_collection,
    get_traces_collection,
)
from app.models import AIAskRequest
from app.pricing import calculate_estimated_cost
from app.tracing import TraceManager


router = APIRouter()
logger = logging.getLogger("task24.routes")


def serialize_value(value):
    if isinstance(value, datetime):
        return value.isoformat()

    return value


def serialize_document(document):
    if document is None:
        return None

    return {
        key: serialize_value(value)
        for key, value in document.items()
        if key not in {"_id", "_start_perf"}
    }


async def serialize_trace(trace):
    result = serialize_document(trace)

    spans = await get_spans_collection().find(
        {
            "trace_id": trace["trace_id"]
        },
        {
            "_id": 0,
            "_start_perf": 0,
        },
    ).sort(
        "created_at",
        1,
    ).to_list(length=None)

    result["spans"] = [
        serialize_document(span)
        for span in spans
    ]

    return result


def pagination(page: int, page_size: int):
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)

    return page, page_size, (page - 1) * page_size


def percentile(
    values: list[float],
    percentile_value: float,
) -> float:
    if not values:
        return 0.0

    if len(values) == 1:
        return round(float(values[0]), 2)

    values = sorted(float(value) for value in values)

    rank = (len(values) - 1) * percentile_value
    lower = int(rank)
    upper = min(lower + 1, len(values) - 1)
    fraction = rank - lower

    return round(
        values[lower]
        + (values[upper] - values[lower]) * fraction,
        2,
    )


@router.get("/")
async def root():
    return {
        "success": True,
        "status_code": 200,
        "data": {
            "message": "Task 24 AI Observability API",
            "docs": "/docs",
        },
    }


@router.get("/health")
async def health():
    await get_traces_collection().database.client.admin.command(
        "ping"
    )

    return {
        "success": True,
        "status_code": 200,
        "data": {
            "status": "healthy",
            "database": "mongodb",
        },
    }


@router.get("/observability/privacy")
async def privacy_status():
    return {
        "success": True,
        "status_code": 200,
        "data": {
            "ai_content_logging_enabled": LOG_AI_CONTENT,
            "prompt_content_stored": LOG_AI_CONTENT,
            "response_content_stored": LOG_AI_CONTENT,
            "metadata_stored": True,
            "message": (
                "Sensitive prompt and response content are not "
                "stored."
                if not LOG_AI_CONTENT
                else (
                    "AI content logging is enabled. "
                    "Sensitive content may be stored."
                )
            ),
        },
    }


@router.post("/ai/ask")
async def ask_ai(
    request: Request,
    body: AIAskRequest,
):
    trace_id = getattr(
        request.state,
        "trace_id",
        None,
    )

    trace = TraceManager(
        trace_id=trace_id
    )

    prompt_tokens = None
    completion_tokens = None
    total_tokens = None
    estimated_cost = None

    prompt_length = len(body.message)
    prompt_version = (
        body.prompt_version or PROMPT_VERSION
    )

    prompt_span = trace.start_span(
        "prompt_build"
    )

    try:
        trace.finish_span(prompt_span)

    except Exception:
        trace.finish_span(
            prompt_span,
            status="failed",
            error_category="INTERNAL_ERROR",
        )
        raise

    llm_span = trace.start_span(
        "openrouter_call"
    )

    try:
        result = call_openrouter(
            body.message
        )

        trace.finish_span(llm_span)

        response_text = result["response"]

        prompt_tokens = result.get(
            "prompt_tokens"
        )

        completion_tokens = result.get(
            "completion_tokens"
        )

        total_tokens = result.get(
            "total_tokens"
        )

        estimated_cost = calculate_estimated_cost(
            prompt_tokens,
            completion_tokens,
        )

        await trace.save_trace(
            request_type="ai_ask",
            model=result.get(
                "model",
                OPENROUTER_MODEL,
            ),
            prompt_version=prompt_version,
            status="success",
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=estimated_cost,
            prompt_length=prompt_length,
            response_length=len(response_text),
            status_code=200,
        )

        logger.info(
            "ai_request_completed "
            "trace_id=%s model=%s status=success",
            trace.trace_id,
            result.get(
                "model",
                OPENROUTER_MODEL,
            ),
        )

        return {
            "success": True,
            "status_code": 200,
            "data": {
                "response": response_text,
                "trace_id": trace.trace_id,
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                },
                "estimated_cost_usd": estimated_cost,
            },
        }

    except AIServiceError as exc:
        trace.finish_span(
            llm_span,
            status="failed",
            error_category=exc.category,
        )

        failure_status = (
            "timeout"
            if exc.category == "OPENROUTER_TIMEOUT"
            else (
                "rate_limited"
                if exc.category == "OPENROUTER_RATE_LIMIT"
                else "failed"
            )
        )

        await trace.save_trace(
            request_type="ai_ask",
            model=OPENROUTER_MODEL,
            prompt_version=prompt_version,
            status=failure_status,
            error_category=exc.category,
            prompt_length=prompt_length,
            status_code=exc.status_code,
        )

        logger.error(
            "ai_request_failed "
            "trace_id=%s error_category=%s",
            trace.trace_id,
            exc.category,
        )

        raise HTTPException(
            status_code=exc.status_code,
            detail={
                "success": False,
                "status_code": exc.status_code,
                "error": exc.category,
                "message": exc.message,
                "trace_id": trace.trace_id,
            },
        ) from exc

    except Exception as exc:
        trace.finish_span(
            llm_span,
            status="failed",
            error_category="INTERNAL_ERROR",
        )

        await trace.save_trace(
            request_type="ai_ask",
            model=OPENROUTER_MODEL,
            prompt_version=prompt_version,
            status="failed",
            error_category="INTERNAL_ERROR",
            prompt_length=prompt_length,
            status_code=500,
        )

        logger.exception(
            "ai_request_internal_error "
            "trace_id=%s",
            trace.trace_id,
        )

        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "status_code": 500,
                "error": "INTERNAL_ERROR",
                "message": "An internal error occurred.",
                "trace_id": trace.trace_id,
            },
        ) from exc


@router.get("/observability/traces/slow")
async def slow_traces(
    page: int = Query(1, ge=1),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
    ),
    threshold_ms: Optional[float] = Query(
        None,
        ge=0,
    ),
):
    page, page_size, skip = pagination(
        page,
        page_size,
    )

    threshold = (
        SLOW_REQUEST_THRESHOLD_MS
        if threshold_ms is None
        else threshold_ms
    )

    query = {
        "total_duration_ms": {
            "$gt": threshold
        }
    }

    traces = get_traces_collection()

    items = await traces.find(
        query,
        {
            "_id": 0
        },
    ).sort(
        "total_duration_ms",
        -1,
    ).skip(
        skip
    ).limit(
        page_size
    ).to_list(
        length=page_size
    )

    total = await traces.count_documents(
        query
    )

    return {
        "success": True,
        "status_code": 200,
        "data": {
            "threshold_ms": threshold,
            "page": page,
            "page_size": page_size,
            "total": total,
            "traces": [
                serialize_document(item)
                for item in items
            ],
        },
    }


@router.get("/observability/traces/failures")
async def failure_traces(
    error_category: Optional[str] = Query(
        None
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
    ),
):
    page, page_size, skip = pagination(
        page,
        page_size,
    )

    query = {
        "status": {
            "$ne": "success"
        }
    }

    if error_category:
        query["error_category"] = error_category

    traces = get_traces_collection()

    items = await traces.find(
        query,
        {
            "_id": 0
        },
    ).sort(
        "start_time",
        -1,
    ).skip(
        skip
    ).limit(
        page_size
    ).to_list(
        length=page_size
    )

    total = await traces.count_documents(
        query
    )

    return {
        "success": True,
        "status_code": 200,
        "data": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "traces": [
                serialize_document(item)
                for item in items
            ],
        },
    }


@router.get("/observability/traces/{trace_id}")
async def get_trace(
    trace_id: str,
):
    trace = await get_traces_collection().find_one(
        {
            "trace_id": trace_id
        }
    )

    if trace is None:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "status_code": 404,
                "error": "TRACE_NOT_FOUND",
                "message": "Trace not found.",
            },
        )

    return {
        "success": True,
        "status_code": 200,
        "data": await serialize_trace(trace),
    }


@router.get("/observability/metrics")
async def get_metrics():
    traces = get_traces_collection()

    total = await traces.count_documents({})

    successful = await traces.count_documents(
        {
            "status": "success"
        }
    )

    failed = await traces.count_documents(
        {
            "status": {
                "$ne": "success"
            }
        }
    )

    docs = await traces.find(
        {},
        {
            "_id": 0,
            "model": 1,
            "prompt_version": 1,
            "total_duration_ms": 1,
            "prompt_tokens": 1,
            "completion_tokens": 1,
            "total_tokens": 1,
            "estimated_cost_usd": 1,
            "status": 1,
            "error_category": 1,
        },
    ).to_list(
        length=None
    )

    latencies = [
        document["total_duration_ms"]
        for document in docs
        if isinstance(
            document.get("total_duration_ms"),
            (int, float),
        )
    ]

    total_tokens = sum(
        document.get("total_tokens") or 0
        for document in docs
    )

    total_cost = sum(
        document.get("estimated_cost_usd") or 0
        for document in docs
    )

    model_groups = {}
    prompt_groups = {}

    for document in docs:
        model_name = (
            document.get("model")
            or "unknown"
        )

        prompt_version = (
            document.get("prompt_version")
            or "unknown"
        )

        model_groups.setdefault(
            model_name,
            [],
        ).append(document)

        prompt_groups.setdefault(
            prompt_version,
            [],
        ).append(document)

    def group_stats(groups):
        result = []

        for name, group in groups.items():
            values = [
                item["total_duration_ms"]
                for item in group
                if isinstance(
                    item.get("total_duration_ms"),
                    (int, float),
                )
            ]

            result.append(
                {
                    "name": name,
                    "requests": len(group),
                    "successful_requests": sum(
                        1
                        for item in group
                        if item.get("status")
                        == "success"
                    ),
                    "failed_requests": sum(
                        1
                        for item in group
                        if item.get("status")
                        != "success"
                    ),
                    "average_latency_ms": (
                        round(
                            sum(values) / len(values),
                            2,
                        )
                        if values
                        else 0.0
                    ),
                    "p50_latency_ms": percentile(
                        values,
                        0.50,
                    ),
                    "p95_latency_ms": percentile(
                        values,
                        0.95,
                    ),
                    "total_tokens": sum(
                        item.get("total_tokens") or 0
                        for item in group
                    ),
                    "estimated_cost_usd": round(
                        sum(
                            item.get(
                                "estimated_cost_usd"
                            )
                            or 0
                            for item in group
                        ),
                        8,
                    ),
                }
            )

        return result

    failure_groups = {}

    for document in docs:
        if document.get("status") != "success":
            category = (
                document.get("error_category")
                or "INTERNAL_ERROR"
            )

            failure_groups[category] = (
                failure_groups.get(category, 0) + 1
            )

    success_rate = (
        round(
            successful / total * 100,
            2,
        )
        if total
        else 0.0
    )

    return {
        "success": True,
        "status_code": 200,
        "data": {
            "total_requests": total,
            "successful_requests": successful,
            "failed_requests": failed,
            "success_rate_percent": success_rate,
            "average_latency_ms": (
                round(
                    sum(latencies) / len(latencies),
                    2,
                )
                if latencies
                else 0.0
            ),
            "p50_latency_ms": percentile(
                latencies,
                0.50,
            ),
            "p95_latency_ms": percentile(
                latencies,
                0.95,
            ),
            "total_tokens": total_tokens,
            "estimated_cost_usd": round(
                total_cost,
                8,
            ),
            "requests_by_model": group_stats(
                model_groups
            ),
            "requests_by_prompt_version": group_stats(
                prompt_groups
            ),
            "failures_by_category": [
                {
                    "error_category": category,
                    "count": count,
                }
                for category, count in sorted(
                    failure_groups.items()
                )
            ],
        },
    }