def test_trace_endpoint_requires_auth(
    client
):

    response = client.get(
        "/observability/traces/test"
    )

    assert response.status_code == 401