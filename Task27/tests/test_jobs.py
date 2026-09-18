def test_job_endpoint_requires_auth(
    client
):

    response = client.get(
        "/jobs/test-job"
    )

    assert response.status_code == 401