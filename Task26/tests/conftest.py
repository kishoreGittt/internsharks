import asyncio
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.queue.fake_redis import FakeRedisQueue
from app.repositories.job_repository import JobRepository
from app.services.ai_service import AIService
from app.services.document_service import DocumentService
from app.services.job_service import JobService
from app.workers.worker import JobWorker


@pytest_asyncio.fixture
async def test_environment(tmp_path: Path):
    repository = JobRepository()
    queue = FakeRedisQueue()

    document_service = DocumentService(
        max_file_size=10 * 1024 * 1024,
    )

    ai_service = AIService(
        api_key="test-key",
        model="test-model",
        base_url="http://test",
    )

    async def fake_analyze_document(
        analysis_type: str,
        document_text: str,
    ):
        if analysis_type == "summary":
            return {
                "summary": "Test summary"
            }

        if analysis_type == "key_points":
            return {
                "key_points": [
                    "Point one",
                    "Point two",
                ]
            }

        return {
            "title": "Test document",
            "summary": "Test summary",
            "main_topics": ["Testing"],
            "key_points": ["Point one"],
        }

    ai_service.analyze_document = fake_analyze_document

    documents_dir = tmp_path / "documents"
    documents_dir.mkdir()

    job_service = JobService(
        repository=repository,
        queue=queue,
        document_service=document_service,
        documents_dir=documents_dir,
    )

    worker = JobWorker(
        worker_id="worker_test",
        queue=queue,
        repository=repository,
        document_service=document_service,
        ai_service=ai_service,
    )

    async def test_lifespan(app):
        worker_task = asyncio.create_task(
            worker.run()
        )

        yield

        worker_task.cancel()

        await asyncio.gather(
            worker_task,
            return_exceptions=True,
        )

    from fastapi import FastAPI
    from app.routes.jobs import router

    app = FastAPI(lifespan=test_lifespan)

    import app.main

    original_service = app.main.job_service
    app.main.job_service = job_service

    app.include_router(router)

    yield app, repository, queue, job_service

    app.main.job_service = original_service


@pytest_asyncio.fixture
async def client(test_environment):
    app, repository, queue, job_service = test_environment

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as async_client:
        yield async_client