import uuid
import time
from datetime import datetime, timezone

from app.storage.mongodb import traces_collection


def create_trace(
    owner_id: str,
    request_type: str
):

    return {
        "trace_id": str(
            uuid.uuid4()
        ),

        "owner_id": owner_id,

        "request_type": request_type,

        "status": "running",

        "started_at":
            datetime.now(
                timezone.utc
            ),

        "spans": [],

        "errors": []
    }


def add_span(
    trace: dict,
    name: str,
    duration_ms: float,
    metadata: dict | None = None
):

    trace["spans"].append(
        {
            "name": name,

            "duration_ms":
                round(
                    duration_ms,
                    2
                ),

            "metadata":
                metadata or {}
        }
    )


async def finish_trace(
    trace: dict,
    status: str = "success",
    error: str | None = None
):

    trace["status"] = status

    trace["finished_at"] = (
        datetime.now(
            timezone.utc
        )
    )

    if error:

        trace["errors"].append(
            {
                "category": error
            }
        )

    await traces_collection.insert_one(
        trace
    )

    return trace