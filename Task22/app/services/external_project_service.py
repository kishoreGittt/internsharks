import time
from app.reliability.errors import RetryableError, NonRetryableError

def get_external_project_status(project_id, failure_mode="success", attempt=1):
    if not project_id:
        raise NonRetryableError("project_id is required", "PROJECT_ID_REQUIRED")

    if failure_mode == "success":
        return {"project_id": project_id, "status": "active", "attempt": attempt}

    if failure_mode == "temporary_failure":
        raise RetryableError("External service temporarily unavailable",
                             "EXTERNAL_SERVICE_UNAVAILABLE", 503)

    if failure_mode == "timeout":
        time.sleep(10)
        return {"project_id": project_id, "status": "active"}

    if failure_mode == "permanent_failure":
        raise NonRetryableError("External project does not exist",
                                "PROJECT_NOT_FOUND", 404)

    raise NonRetryableError("Unknown failure mode", "INVALID_FAILURE_MODE")
