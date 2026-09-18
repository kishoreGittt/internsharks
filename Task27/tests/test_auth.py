def test_register_endpoint_exists(
    client
):

    response = client.post(
        "/auth/register",
        json={
            "email":
                "test@example.com",

            "password":
                "Password123!"
        }
    )

    assert response.status_code in {
        201,
        400,
        409,
        500
    }