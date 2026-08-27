def test_successful_registration(client):

    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "Test@12345",
            "full_name": "Test User",
            "phone": "9876543210",
            "department": "IT",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["success"] is True
    assert body["message"] == "User registered successfully"

    assert body["data"]["email"] == "testuser@example.com"
    assert body["data"]["role"] == "user"

    assert "password" not in body["data"]


def test_duplicate_registration(client):

    payload = {
        "username": "testuser",
        "email": "duplicate@example.com",
        "password": "Test@12345",
        "full_name": "Test User",
    }

    first = client.post(
        "/auth/register",
        json=payload
    )

    assert first.status_code == 201

    second = client.post(
        "/auth/register",
        json=payload
    )

    assert second.status_code == 409

    body = second.json()

    assert body["success"] is False
    assert body["status_code"] == 409
    assert body["error"] == "CONFLICT"


def test_invalid_registration(client):

    response = client.post(
        "/auth/register",
        json={
            "username": "a",
            "email": "invalid-email",
            "password": "123",
            "full_name": "",
        },
    )

    assert response.status_code == 422

    body = response.json()

    assert body["success"] is False
    assert body["status_code"] == 422
    assert body["error"] == "VALIDATION_ERROR"


def test_successful_login(client):

    client.post(
        "/auth/register",
        json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "Test@12345",
            "full_name": "Login User",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "Test@12345",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True

    assert "access_token" in body["data"]
    assert "refresh_token" in body["data"]
    assert body["data"]["token_type"] == "bearer"


def test_incorrect_credentials(client):

    client.post(
        "/auth/register",
        json={
            "username": "loginuser",
            "email": "wrong@example.com",
            "password": "Test@12345",
            "full_name": "Login User",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "WrongPassword",
        },
    )

    assert response.status_code == 401

    body = response.json()

    assert body["success"] is False
    assert body["status_code"] == 401
    assert body["error"] == "UNAUTHORIZED"


def test_protected_endpoint_without_token(client):

    response = client.get(
        "/users/me"
    )

    assert response.status_code == 401

    body = response.json()

    assert body["success"] is False
    assert body["status_code"] == 401
    assert body["error"] == "UNAUTHORIZED"


def test_invalid_access_token(client):

    response = client.get(
        "/users/me",
        headers={
            "Authorization": "Bearer invalid-token"
        },
    )

    assert response.status_code == 401

    body = response.json()

    assert body["success"] is False
    assert body["status_code"] == 401
    assert body["error"] == "UNAUTHORIZED"


def test_refresh_token(client):

    client.post(
        "/auth/register",
        json={
            "username": "refreshuser",
            "email": "refresh@example.com",
            "password": "Test@12345",
            "full_name": "Refresh User",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "refresh@example.com",
            "password": "Test@12345",
        },
    )

    refresh_token = (
        login_response.json()["data"]["refresh_token"]
    )

    response = client.post(
        "/auth/refresh",
        params={
            "refresh_token": refresh_token
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert "access_token" in body["data"]


def test_invalid_refresh_token(client):

    response = client.post(
        "/auth/refresh",
        params={
            "refresh_token": "invalid-refresh-token"
        },
    )

    assert response.status_code == 401

    body = response.json()

    assert body["success"] is False
    assert body["status_code"] == 401