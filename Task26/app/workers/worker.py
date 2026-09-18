import asyncio
import logging
from datetime import datetime, timezone

from app.models.job import JobStatus
from app.queue.fake_redis import FakeRedisQueue
from app.repositories.job_repository import JobRepository
from app.services.ai_service import AIService
from app.services.document_service import DocumentService


logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class JobWorker:
    def __init__(
        self,
        worker_id: str,
        queue: FakeRedisQueue,
        repository: JobRepository,
        document_service: DocumentService,
        ai_service: AIService,
    ) -> None:
        self.worker_id = worker_id
        self.queue = queue
        self.repository = repository
        self.document_service = document_service
        self.ai_service = ai_service

    async def process_job(self, job_id: str) -> None:
        job = await self.repository.get_job(job_id)

        if job is None:
            logger.warning(
                "%s: Job %s not found",
                self.worker_id,
                job_id,
            )
            return

        if job.status != JobStatus.QUEUED:
            logger.info(
                "%s: Skipping job %s with status %s",
                self.worker_id,
                job_id,
                job.status.value,
            )
            return

        updated_job = await self.repository.update_job(
            job_id,
            status=JobStatus.PROCESSING,
            started_at=utc_now(),
            processed_by=self.worker_id,
        )

        if updated_job is None:
            return

        try:
            document_text = self.document_service.extract_text(
                updated_job.file_path
            )

            result = await self.ai_service.analyze_document(
                analysis_type=updated_job.analysis_type,
                document_text=document_text,
            )

            await self.repository.update_job(
                job_id,
                status=JobStatus.COMPLETED,
                result=result,
                completed_at=utc_now(),
            )

            logger.info(
                "%s completed job %s",
                self.worker_id,
                job_id,
            )

        except Exception as exc:
            logger.exception(
                "%s failed job %s",
                self.worker_id,
                job_id,
            )

            await self.repository.update_job(
                job_id,
                status=JobStatus.FAILED,
                error=str(exc)[:1000],
                completed_at=utc_now(),
            )

    async def run(self) -> None:
        logger.info(
            "%s started",
            self.worker_id,
        )

        while True:
            job_id = await self.queue.dequeue()

            try:
                await self.process_job(job_id)

            except asyncio.CancelledError:
                raise

            except Exception:
                logger.exception(
                    "%s encountered an unexpected error",
                    self.worker_id,
                )

            finally:
                self.queue.task_done()