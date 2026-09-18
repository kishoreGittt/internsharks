import asyncio
from typing import Any

from app.models.job import JobRecord, JobStatus


class JobRepository:
    def __init__(self) -> None:
        self._jobs: dict[str, JobRecord] = {}
        self._lock = asyncio.Lock()

    async def create_job(self, job: JobRecord) -> JobRecord:
        async with self._lock:
            self._jobs[job.job_id] = job.model_copy(deep=True)
            return job.model_copy(deep=True)

    async def get_job(self, job_id: str) -> JobRecord | None:
        async with self._lock:
            job = self._jobs.get(job_id)

            if job is None:
                return None

            return job.model_copy(deep=True)

    async def update_job(
        self,
        job_id: str,
        **updates: Any,
    ) -> JobRecord | None:
        async with self._lock:
            job = self._jobs.get(job_id)

            if job is None:
                return None

            updated_job = job.model_copy(update=updates, deep=True)
            self._jobs[job_id] = updated_job

            return updated_job.model_copy(deep=True)

    async def list_jobs(
        self,
        status: JobStatus | None = None,
        analysis_type: str | None = None,
    ) -> list[JobRecord]:
        async with self._lock:
            jobs = list(self._jobs.values())

            if status is not None:
                jobs = [
                    job
                    for job in jobs
                    if job.status == status
                ]

            if analysis_type is not None:
                jobs = [
                    job
                    for job in jobs
                    if job.analysis_type == analysis_type
                ]

            jobs.sort(
                key=lambda job: job.created_at,
                reverse=True,
            )

            return [
                job.model_copy(deep=True)
                for job in jobs
            ]

    async def count(self) -> int:
        async with self._lock:
            return len(self._jobs)