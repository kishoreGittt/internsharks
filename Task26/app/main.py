import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.config import settings
from app.queue.fake_redis import FakeRedisQueue
from app.repositories.job_repository import JobRepository
from app.routes.jobs import router
from app.services.ai_service import AIService
from app.services.document_service import DocumentService
from app.services.job_service import JobService
from app.workers.worker import JobWorker


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(message)s"
    ),
)

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = BASE_DIR / "data" / "documents"

DOCUMENTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

repository = JobRepository()
queue = FakeRedisQueue()

document_service = DocumentService(
    max_file_size=settings.max_file_size,
)

ai_service = AIService(
    api_key=settings.openrouter_api_key,
    model=settings.openrouter_model,
    base_url=settings.openrouter_base_url,
    simulated_delay=(
        settings.simulated_processing_delay_seconds
    ),
    simulate_failure=settings.simulate_ai_failure,
)

job_service = JobService(
    repository=repository,
    queue=queue,
    document_service=document_service,
    documents_dir=DOCUMENTS_DIR,
)

worker_tasks: list[asyncio.Task] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    global worker_tasks

    worker_tasks = []

    for index in range(settings.worker_count):
        worker = JobWorker(
            worker_id=f"worker_{index + 1}",
            queue=queue,
            repository=repository,
            document_service=document_service,
            ai_service=ai_service,
        )

        task = asyncio.create_task(
            worker.run(),
            name=f"worker_{index + 1}",
        )

        worker_tasks.append(task)

    logger.info(
        "Started %s workers",
        settings.worker_count,
    )

    yield

    logger.info("Stopping workers")

    for task in worker_tasks:
        task.cancel()

    await asyncio.gather(
        *worker_tasks,
        return_exceptions=True,
    )

    worker_tasks.clear()

    logger.info("All workers stopped")


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/")
async def root():
    return {
        "success": True,
        "status_code": 200,
        "message": "Task 26 Async AI Jobs API is running",
    }


@app.get("/health")
async def health():
    return {
        "success": True,
        "status_code": 200,
        "data": {
            "status": "healthy",
            "workers": settings.worker_count,
        },
    }