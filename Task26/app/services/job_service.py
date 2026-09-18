import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import HTTPException, UploadFile

from app.models.job import JobRecord, JobStatus
from app.queue.fake_redis import FakeRedisQueue
from app.repositories.job_repository import JobRepository
from app.services.document_service import DocumentService


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class JobService:
    def __init__(
        self,
        repository: JobRepository,
        queue: FakeRedisQueue,
        document_service: DocumentService,
        documents_dir: Path,
    ) -> None:
        self.repository = repository
        self.queue = queue
        self.document_service = document_service
        self.documents_dir = documents_dir

    async def submit_job(
        self,
        upload_file: UploadFile,
        analysis_type: str,
    ) -> JobRecord:
        if analysis_type not in {
            "summary",
            "key_points",
            "document_analysis",
        }:
            raise HTTPException(
                status_code=400,
                detail="Invalid analysis_type",
            )

        if not upload_file.filename:
            raise HTTPException(
                status_code=400,
                detail="File name is required",
            )

        original_path = self.document_service.validate_filename(
            upload_file.filename
        )

        job_id = f"job_{uuid.uuid4().hex}"

        destination = self.documents_dir / (
            f"{job_id}{original_path.suffix.lower()}"
        )

        await self.document_service.save_upload(
            upload_file=upload_file,
            destination=destination,
        )

        job = JobRecord(
            job_id=job_id,
            file_name=original_path.name,
            file_path=str(destination),
            analysis_type=analysis_type,
            status=JobStatus.QUEUED,
        )

        await self.repository.create_job(job)
        await self.queue.enqueue(job_id)

        return job

    async def get_job_or_404(
        self,
        job_id: str,
    ) -> JobRecord:
        job = await self.repository.get_job(job_id)

        if job is None:
            raise HTTPException(
                status_code=404,
                detail="Job not found",
            )

        return job

    async def cancel_job(
        self,
        job_id: str,
    ) -> JobRecord:
        job = await self.get_job_or_404(job_id)

        if job.status != JobStatus.QUEUED:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Only queued jobs can be cancelled"
                ),
            )

        updated_job = await self.repository.update_job(
            job_id,
            status=JobStatus.CANCELLED,
            completed_at=utc_now(),
        )

        if updated_job is None:
            raise HTTPException(
                status_code=404,
                detail="Job not found",
            )

        return updated_job

    def serialize_job(
        self,
        job: JobRecord,
        include_result: bool = True,
    ) -> dict[str, Any]:
        data = {
            "job_id": job.job_id,
            "file_name": job.file_name,
            "analysis_type": job.analysis_type,
            "status": job.status.value,
            "processed_by": job.processed_by,
            "created_at": job.created_at.isoformat(),
            "started_at": (
                job.started_at.isoformat()
                if job.started_at
                else None
            ),
            "completed_at": (
                job.completed_at.isoformat()
                if job.completed_at
                else None
            ),
        }

        if include_result:
            data["result"] = job.result

        if job.error:
            data["error"] = job.error

        return data