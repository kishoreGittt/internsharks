from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.models.job import (
    JobListResponse,
    JobResponse,
    JobStatus,
    JobSubmitResponse,
    QueueResponse,
)
from app.services.job_service import JobService


router = APIRouter(
    prefix="/jobs",
    tags=["Async AI Jobs"],
)


def get_service() -> JobService:
    from app.main import job_service

    return job_service


@router.post(
    "/document-analysis",
    response_model=JobSubmitResponse,
    status_code=202,
)
async def submit_document_analysis(
    file: Annotated[UploadFile, File(...)],
    analysis_type: Annotated[str, Form(...)],
) -> JobSubmitResponse:
    service = get_service()

    job = await service.submit_job(
        upload_file=file,
        analysis_type=analysis_type,
    )

    return JobSubmitResponse(
        data={
            "job_id": job.job_id,
            "status": job.status.value,
        }
    )


@router.get(
    "/queue/status",
    response_model=QueueResponse,
)
async def queue_status() -> QueueResponse:
    service = get_service()

    return QueueResponse(
        data={
            "queued_jobs": service.queue.size(),
        }
    )


@router.get(
    "/{job_id}/result",
    response_model=JobResponse,
)
async def get_job_result(
    job_id: str,
) -> JobResponse:
    service = get_service()

    job = await service.get_job_or_404(job_id)

    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=409,
            detail=(
                "Job result is not available. "
                f"Current status: {job.status.value}"
            ),
        )

    return JobResponse(
        data={
            "job_id": job.job_id,
            "status": job.status.value,
            "result": job.result,
        }
    )


@router.get(
    "",
    response_model=JobListResponse,
)
async def list_jobs(
    status: JobStatus | None = None,
    analysis_type: str | None = None,
) -> JobListResponse:
    service = get_service()

    jobs = await service.repository.list_jobs(
        status=status,
        analysis_type=analysis_type,
    )

    return JobListResponse(
        data={
            "jobs": [
                service.serialize_job(job)
                for job in jobs
            ],
            "count": len(jobs),
        }
    )


@router.post(
    "/{job_id}/cancel",
    response_model=JobResponse,
)
async def cancel_job(
    job_id: str,
) -> JobResponse:
    service = get_service()

    job = await service.cancel_job(job_id)

    return JobResponse(
        data={
            "job_id": job.job_id,
            "status": job.status.value,
        }
    )


@router.get(
    "/{job_id}",
    response_model=JobResponse,
)
async def get_job(
    job_id: str,
) -> JobResponse:
    service = get_service()

    job = await service.get_job_or_404(job_id)

    return JobResponse(
        data=service.serialize_job(job)
    )