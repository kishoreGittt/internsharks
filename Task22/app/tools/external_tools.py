from app.config import EXTERNAL_TOOL_TIMEOUT
from app.services.external_project_service import get_external_project_status
from app.reliability.retry import retry_call
from app.reliability.timeout import run_with_timeout

def resilient_external_status(project_id, failure_mode="success", trace=None):
    def operation(attempt):
        if trace is not None:
            trace.append({
                "tool": "get_external_project_status",
                "attempt": attempt,
                "status": "started"
            })
        try:
            result = run_with_timeout(
                lambda: get_external_project_status(project_id, failure_mode, attempt),
                EXTERNAL_TOOL_TIMEOUT
            )
            if trace is not None:
                trace.append({
                    "tool": "get_external_project_status",
                    "attempt": attempt,
                    "status": "success"
                })
            return result
        except Exception as exc:
            if trace is not None:
                trace.append({
                    "tool": "get_external_project_status",
                    "attempt": attempt,
                    "status": getattr(exc, "code", "failure"),
                    "message": str(exc)
                })
            raise

    return retry_call(operation)
