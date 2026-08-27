def register_and_login(client):

    client.post(
        "/auth/register",
        json={
            "username": "user1",
            "email": "user1@example.com",
            "password": "Test@12345",
            "full_name": "User One",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "user1@example.com",
            "password": "Test@12345",
        },
    )

    return response.json()["data"]["access_token"]


def test_get_my_profile(client):

    token = register_and_login(client)

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["data"]["email"] == "user1@example.com"

    assert "password" not in body["data"]


def test_update_my_profile(client):

    token = register_and_login(client)

    response = client.put(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "full_name": "Updated User",
            "department": "Engineering",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["data"]["full_name"] == "Updated User"


def test_user_cannot_access_admin_users(client):

    token = register_and_login(client)

    response = client.get(
        "/admin/users",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 403

    body = response.json()

    assert body["success"] is False
    assert body["status_code"] == 403
    assert body["error"] == "FORBIDDEN"