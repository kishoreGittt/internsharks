import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from app.database import get_spans_collection, get_traces_collection

def generate_trace_id() -> str:
    return f"trace_{uuid.uuid4().hex}"

def generate_span_id() -> str:
    return f"span_{uuid.uuid4().hex}"

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class TraceManager:
    def __init__(self, trace_id: Optional[str] = None):
        self.trace_id = trace_id or generate_trace_id()
        self.start_time = utc_now()
        self.start_perf = time.perf_counter()
        self.spans = []

    def start_span(self, name: str) -> dict[str, Any]:
        span = {
            "span_id": generate_span_id(),
            "trace_id": self.trace_id,
            "name": name,
            "status": "running",
            "_start_perf": time.perf_counter(),
        }
        self.spans.append(span)
        return span

    def finish_span(
        self,
        span: dict[str, Any],
        status: str = "success",
        error_category: Optional[str] = None,
    ):
        duration_ms = (time.perf_counter() - span["_start_perf"]) * 1000
        span["status"] = status
        span["duration_ms"] = round(duration_ms, 2)
        span["end_time"] = utc_now()
        if error_category:
            span["error_category"] = error_category
        span.pop("_start_perf", None)

    def total_duration_ms(self) -> float:
        return round((time.perf_counter() - self.start_perf) * 1000, 2)

    def save_trace(
        self,
        *,
        request_type: str,
        model: str,
        prompt_version: str,
        status: str,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
        estimated_cost_usd: Optional[float] = None,
        error_category: Optional[str] = None,
        prompt_length: Optional[int] = None,
        response_length: Optional[int] = None,
        status_code: int = 200,
    ):
        trace_document = {
            "trace_id": self.trace_id,
            "request_type": request_type,
            "model": model,
            "prompt_version": prompt_version,
            "status": status,
            "status_code": status_code,
            "start_time": self.start_time,
            "end_time": utc_now(),
            "total_duration_ms": self.total_duration_ms(),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": estimated_cost_usd,
            "error_category": error_category,
            "prompt_length": prompt_length,
            "response_length": response_length,
            "created_at": utc_now(),
        }

        traces = get_traces_collection()
        spans = get_spans_collection()
        traces.insert_one(trace_document)

        for span in self.spans:
            spans.insert_one({**span, "created_at": utc_now()})

        return trace_document
