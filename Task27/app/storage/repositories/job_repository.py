from datetime import datetime, timezone
from typing import Optional

from pymongo import ReturnDocument

from app.storage.mongodb import jobs_collection


def utc_now():
    return datetime.now(timezone.utc)


async def create_job(
    job_id: str,
    owner_id: str,
    document_id: str,
    status: str = "queued",
    progress: int = 0,
    error: Optional[str] = None,
):
    job = {
        "job_id": job_id,
        "user_id": owner_id,
        "owner_id": owner_id,
        "document_id": document_id,
        "status": status,
        "progress": progress,
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }

    if error:
        job["error"] = error

    await jobs_collection.insert_one(job)

    job.pop("_id", None)

    return job


async def get_job(
    user_id: str,
    job_id: str,
) -> Optional[dict]:
    """
    Find a job belonging to the authenticated user.
    """

    job = await jobs_collection.find_one(
        {
            "job_id": job_id,
            "$or": [
                {"user_id": user_id},
                {"owner_id": user_id},
            ],
        },
        {
            "_id": 0,
        },
    )

    return job


async def claim_next_job() -> Optional[dict]:
    """
    Claim the oldest queued job.
    """

    job = await jobs_collection.find_one_and_update(
        {
            "status": "queued"
        },
        {
            "$set": {
                "status": "processing",
                "progress": 10,
                "updated_at": utc_now(),
            }
        },
        sort=[("created_at", 1)],
        return_document=ReturnDocument.AFTER,
    )

    if job:
        job.pop("_id", None)

    return job


async def update_job(
    job_id: str,
    status: str,
    progress: Optional[int] = None,
    error: Optional[str] = None,
):
    update_data = {
        "status": status,
        "updated_at": utc_now(),
    }

    if progress is not None:
        update_data["progress"] = progress

    if error:
        update_data["error"] = error

    update = {
        "$set": update_data
    }

    if not error:
        update["$unset"] = {
            "error": ""
        }

    result = await jobs_collection.update_one(
        {"job_id": job_id},
        update,
    )

    return result.modified_count > 0


async def delete_job(
    user_id: str,
    job_id: str,
):
    result = await jobs_collection.delete_one(
        {
            "job_id": job_id,
            "$or": [
                {"user_id": user_id},
                {"owner_id": user_id},
            ],
        }
    )

    return result.deleted_count > 0