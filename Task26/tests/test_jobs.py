import asyncio

import pytest


@pytest.mark.asyncio
async def test_job_submission_returns_202(client):
    response = await client.post(
        "/jobs/document-analysis",
        files={
            "file": (
                "test.txt",
                b"This is a test document.",
                "text/plain",
            )
        },
        data={
            "analysis_type": "summary",
        },
    )

    assert response.status_code == 202

    body = response.json()

    assert body["success"] is True
    assert body["status_code"] == 202
    assert body["data"]["job_id"].startswith("job_")
    assert body["data"]["status"] == "queued"


@pytest.mark.asyncio
async def test_job_completes(client):
    response = await client.post(
        "/jobs/document-analysis",
        files={
            "file": (
                "test.txt",
                b"This is a test document.",
                "text/plain",
            )
        },
        data={
            "analysis_type": "summary",
        },
    )

    job_id = response.json()["data"]["job_id"]

    for _ in range(50):
        status_response = await client.get(
            f"/jobs/{job_id}"
        )

        status = (
            status_response.json()["data"]["status"]
        )

        if status == "completed":
            break

        await asyncio.sleep(0.05)

    assert status == "completed"

    result_response = await client.get(
        f"/jobs/{job_id}/result"
    )

    assert result_response.status_code == 200

    result = result_response.json()["data"]["result"]

    assert result["summary"] == "Test summary"


@pytest.mark.asyncio
async def test_key_points_result(client):
    response = await client.post(
        "/jobs/document-analysis",
        files={
            "file": (
                "test.txt",
                b"Important information.",
                "text/plain",
            )
        },
        data={
            "analysis_type": "key_points",
        },
    )

    job_id = response.json()["data"]["job_id"]

    for _ in range(50):
        result_response = await client.get(
            f"/jobs/{job_id}/result"
        )

        if result_response.status_code == 200:
            break

        await asyncio.sleep(0.05)

    assert result_response.status_code == 200

    data = result_response.json()["data"]

    assert data["result"]["key_points"] == [
        "Point one",
        "Point two",
    ]


@pytest.mark.asyncio
async def test_invalid_analysis_type(client):
    response = await client.post(
        "/jobs/document-analysis",
        files={
            "file": (
                "test.txt",
                b"Test document",
                "text/plain",
            )
        },
        data={
            "analysis_type": "invalid",
        },
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_unsupported_file(client):
    response = await client.post(
        "/jobs/document-analysis",
        files={
            "file": (
                "test.docx",
                b"Test document",
                "application/octet-stream",
            )
        },
        data={
            "analysis_type": "summary",
        },
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_job_not_found(client):
    response = await client.get(
        "/jobs/job_does_not_exist"
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_queue_status(client):
    response = await client.get(
        "/jobs/queue/status"
    )

    assert response.status_code == 200

    data = response.json()["data"]

    assert "queued_jobs" in data


@pytest.mark.asyncio
async def test_list_jobs(client):
    response = await client.post(
        "/jobs/document-analysis",
        files={
            "file": (
                "test.txt",
                b"Test document",
                "text/plain",
            )
        },
        data={
            "analysis_type": "summary",
        },
    )

    assert response.status_code == 202

    list_response = await client.get(
        "/jobs"
    )

    assert list_response.status_code == 200

    data = list_response.json()["data"]

    assert data["count"] >= 1


@pytest.mark.asyncio
async def test_cancel_queued_job(
    test_environment,
):
    app, repository, queue, job_service = test_environment

    from fastapi import FastAPI
    from httpx import ASGITransport, AsyncClient

    original_worker = None

    # Directly test the service cancellation logic.
    from fastapi import UploadFile
    from io import BytesIO

    upload = UploadFile(
        filename="cancel.txt",
        file=BytesIO(b"Test document"),
    )

    job = await job_service.submit_job(
        upload_file=upload,
        analysis_type="summary",
    )

    cancelled = await job_service.cancel_job(
        job.job_id
    )

    assert cancelled.status.value == "cancelled"


@pytest.mark.asyncio
async def test_two_jobs_have_unique_ids(client):
    response_1 = await client.post(
        "/jobs/document-analysis",
        files={
            "file": (
                "one.txt",
                b"First document",
                "text/plain",
            )
        },
        data={
            "analysis_type": "summary",
        },
    )

    response_2 = await client.post(
        "/jobs/document-analysis",
        files={
            "file": (
                "two.txt",
                b"Second document",
                "text/plain",
            )
        },
        data={
            "analysis_type": "summary",
        },
    )

    job_id_1 = response_1.json()["data"]["job_id"]
    job_id_2 = response_2.json()["data"]["job_id"]

    assert job_id_1 != job_id_2