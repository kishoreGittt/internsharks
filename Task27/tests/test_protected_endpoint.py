def test_protected_endpoint_requires_auth(
    client
):

    response = client.get(
        "/users/me"
    )

    assert response.status_code == 401