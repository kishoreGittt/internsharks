from datetime import datetime, timezone
from typing import Any

from bson import ObjectId

from app.reliability.errors import AgentError
from app.tools.external_tools import get_external_project_status


def utc_now():
    return datetime.now(timezone.utc)


class ProjectService:
    def __init__(self, database):
        self.database = database
        self.runs_collection = database["runs"]
        self.actions_collection = database["actions"]

    def create_run(self, payload: dict[str, Any]) -> str:
        run_document = {
            "status": "running",
            "request": payload,
            "attempt_count": 0,
            "last_failure": None,
            "result": None,
            "error_code": None,
            "error_message": None,
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }

        result = self.runs_collection.insert_one(run_document)

        return str(result.inserted_id)

    def update_run(
        self,
        run_id: str,
        values: dict[str, Any],
    ):
        self.runs_collection.update_one(
            {
                "_id": ObjectId(run_id),
            },
            {
                "$set": {
                    **values,
                    "updated_at": utc_now(),
                }
            },
        )

    def get_run(self, run_id: str):
        try:
            object_id = ObjectId(run_id)
        except Exception:
            return None

        return self.runs_collection.find_one(
            {
                "_id": object_id,
            }
        )

    def save_attempt(
        self,
        run_id: str,
        attempt_number: int,
        status: str,
        error_message: str | None = None,
        result: dict | None = None,
    ):
        attempt_document = {
            "run_id": run_id,
            "attempt_number": attempt_number,
            "status": status,
            "error_message": error_message,
            "result": result,
            "created_at": utc_now(),
        }

        self.actions_collection.insert_one(attempt_document)

        update_values = {
            "attempt_count": attempt_number,
        }

        if error_message is not None:
            update_values["last_failure"] = error_message

        if status == "success":
            update_values.update(
                {
                    "status": "completed",
                    "result": result,
                    "error_code": None,
                    "error_message": None,
                }
            )

        elif status == "retrying":
            update_values["status"] = "retrying"

        elif status == "failed":
            update_values["status"] = "failed"

        self.update_run(
            run_id,
            update_values,
        )

    def execute_run(self, run_id: str):
        run = self.get_run(run_id)

        if not run:
            raise AgentError(
                message="Run not found",
                code="RUN_NOT_FOUND",
                retryable=False,
                status_code=404,
            )

        payload = run.get("request", {})

        project_id = payload.get(
            "project_id",
            "project-001",
        )

        failure_mode = payload.get(
            "failure_mode",
            "success",
        )

        max_retries = payload.get(
            "max_retries",
            3,
        )

        total_attempts = max_retries + 1

        for attempt_number in range(
            1,
            total_attempts + 1,
        ):
            self.save_attempt(
                run_id=run_id,
                attempt_number=attempt_number,
                status="started",
            )

            try:
                result = get_external_project_status(
                    project_id=project_id,
                    failure_mode=failure_mode,
                )

                self.save_attempt(
                    run_id=run_id,
                    attempt_number=attempt_number,
                    status="success",
                    result=result,
                )

                return result

            except AgentError as error:
                self.save_attempt(
                    run_id=run_id,
                    attempt_number=attempt_number,
                    status="failed",
                    error_message=error.message,
                )

                # Non-retryable errors stop immediately.
                if not error.retryable:
                    self.update_run(
                        run_id,
                        {
                            "status": "failed",
                            "error_code": error.code,
                            "error_message": error.message,
                        },
                    )

                    raise

                # Retryable error but no attempts remain.
                if attempt_number >= total_attempts:
                    self.update_run(
                        run_id,
                        {
                            "status": "partially_completed",
                            "error_code": error.code,
                            "error_message": error.message,
                        },
                    )

                    # Important:
                    # Preserve the original error code and HTTP status.
                    #
                    # Timeout:
                    #   code = EXTERNAL_TIMEOUT
                    #   status = 504
                    #
                    # Temporary failure:
                    #   code = EXTERNAL_TEMPORARY_FAILURE
                    #   status = 503
                    raise AgentError(
                        message=error.message,
                        code=error.code,
                        retryable=False,
                        status_code=error.status_code,
                    )

                self.update_run(
                    run_id,
                    {
                        "status": "retrying",
                        "error_code": error.code,
                        "error_message": error.message,
                    },
                )

                # Exponential backoff.
                import time

                delay = 0.5 * (
                    2 ** (attempt_number - 1)
                )

                time.sleep(delay)

        raise AgentError(
            message="Run failed",
            code="RUN_FAILED",
            retryable=False,
            status_code=500,
        )