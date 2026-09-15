import time
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.reliability.errors import AgentError
from app.tools.external_tools import (
    get_external_project_status,
)


def utc_now():
    return datetime.now(timezone.utc)


class ProjectService:
    def __init__(self, database):
        self.database = database

        self.runs_collection = database["runs"]
        self.actions_collection = database["actions"]
        self.projects_collection = database["projects"]

        self.actions_collection.create_index(
            "idempotency_key",
            unique=True,
            sparse=True,
        )

    def create_run(
        self,
        payload: dict[str, Any],
    ) -> str:
        now = utc_now()

        document = {
            "status": "running",
            "request": payload,
            "attempt_count": 0,
            "last_failure": None,
            "error_code": None,
            "error_message": None,
            "result": None,
            "created_at": now,
            "updated_at": now,
        }

        result = self.runs_collection.insert_one(
            document
        )

        return str(result.inserted_id)

    def get_run(self, run_id: str):
        try:
            object_id = ObjectId(run_id)
        except Exception:
            return None

        return self.runs_collection.find_one(
            {"_id": object_id}
        )

    def update_run(
        self,
        run_id: str,
        values: dict[str, Any],
    ):
        try:
            object_id = ObjectId(run_id)
        except Exception:
            return

        self.runs_collection.update_one(
            {"_id": object_id},
            {
                "$set": {
                    **values,
                    "updated_at": utc_now(),
                }
            },
        )

    def save_attempt(
        self,
        run_id: str,
        attempt_number: int,
        status: str,
        error_message: str | None = None,
        error_code: str | None = None,
        result: dict | None = None,
    ):
        attempt_document = {
            "run_id": run_id,
            "attempt_number": attempt_number,
            "status": status,
            "error_code": error_code,
            "error_message": error_message,
            "result": result,
            "created_at": utc_now(),
        }

        self.actions_collection.insert_one(
            attempt_document
        )

        values = {
            "attempt_count": attempt_number,
        }

        if error_message:
            values["last_failure"] = error_message

        if status == "success":
            values.update(
                {
                    "status": "completed",
                    "result": result,
                    "error_code": None,
                    "error_message": None,
                }
            )

        self.update_run(
            run_id,
            values,
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

        max_retries = int(
            payload.get(
                "max_retries",
                3,
            )
        )

        total_attempts = max_retries + 1

        saved_attempt_count = int(
            run.get(
                "attempt_count",
                0,
            )
        )

        start_attempt = saved_attempt_count + 1

        if start_attempt > total_attempts:
            raise AgentError(
                message="Retry limit already exhausted",
                code="RETRY_EXHAUSTED",
                retryable=False,
                status_code=503,
            )

        for attempt_number in range(
            start_attempt,
            total_attempts + 1,
        ):
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
                    error_code=error.code,
                    error_message=error.message,
                )

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

                if attempt_number >= total_attempts:
                    self.update_run(
                        run_id,
                        {
                            "status": "partially_completed",
                            "error_code": error.code,
                            "error_message": error.message,
                        },
                    )

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

                backoff_seconds = 0.5 * (
                    2 ** (attempt_number - 1)
                )

                time.sleep(backoff_seconds)

        raise AgentError(
            message="Run failed",
            code="RUN_FAILED",
            retryable=False,
            status_code=500,
        )

    def execute_idempotent_action(
        self,
        run_id: str,
        action_id: str,
        project_name: str,
    ):
        idempotency_key = (
            f"{run_id}:{action_id}"
        )

        existing_action = (
            self.actions_collection.find_one(
                {
                    "idempotency_key": idempotency_key,
                }
            )
        )

        if existing_action:
            return {
                "created": False,
                "duplicate": True,
                "idempotency_key": idempotency_key,
                "result": existing_action.get(
                    "result"
                ),
            }

        project_document = {
            "project_name": project_name,
            "created_by_run_id": run_id,
            "created_by_action_id": action_id,
            "created_at": utc_now(),
        }

        try:
            project_result = (
                self.projects_collection.insert_one(
                    project_document
                )
            )

            result = {
                "project_id": str(
                    project_result.inserted_id
                ),
                "project_name": project_name,
            }

            self.actions_collection.insert_one(
                {
                    "run_id": run_id,
                    "action_id": action_id,
                    "idempotency_key": idempotency_key,
                    "status": "completed",
                    "result": result,
                    "created_at": utc_now(),
                }
            )

            return {
                "created": True,
                "duplicate": False,
                "idempotency_key": idempotency_key,
                "result": result,
            }

        except DuplicateKeyError:
            existing_action = (
                self.actions_collection.find_one(
                    {
                        "idempotency_key": idempotency_key,
                    }
                )
            )

            return {
                "created": False,
                "duplicate": True,
                "idempotency_key": idempotency_key,
                "result": (
                    existing_action.get("result")
                    if existing_action
                    else None
                ),
            }