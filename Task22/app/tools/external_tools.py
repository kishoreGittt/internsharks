import time

from app.reliability.errors import AgentError


def get_external_project_status(
    project_id: str,
    failure_mode: str = "success",
):
    """
    Simulated external project-status service.

    Supported modes:
    - success
    - temporary_failure
    - timeout
    - permanent_failure
    """

    if failure_mode == "success":
        return {
            "project_id": project_id,
            "status": "active",
            "source": "external_project_service",
        }

    if failure_mode == "temporary_failure":
        raise AgentError(
            message="Temporary external service failure",
            code="EXTERNAL_TEMPORARY_FAILURE",
            retryable=True,
            status_code=503,
        )

    if failure_mode == "timeout":
        time.sleep(10)

        raise AgentError(
            message="External service timed out",
            code="EXTERNAL_TIMEOUT",
            retryable=True,
            status_code=504,
        )

    if failure_mode == "permanent_failure":
        raise AgentError(
            message="Project does not exist in external service",
            code="PROJECT_NOT_FOUND",
            retryable=False,
            status_code=404,
        )

    raise AgentError(
        message=f"Unknown failure mode: {failure_mode}",
        code="INVALID_FAILURE_MODE",
        retryable=False,
        status_code=400,
    )