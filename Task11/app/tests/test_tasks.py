def create_user_and_get_token(
    client,
    email="taskuser@example.com"
):

    client.post(
        "/auth/register",
        json={
            "username": "taskuser",
            "email": email,
            "password": "Test@12345",
            "full_name": "Task User",
        },
    )

    login = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "Test@12345",
        },
    )

    return login.json()["data"]["access_token"]


def create_task(client, token):

    response = client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Test Task",
            "description": "Testing task creation",
            "status": "todo",
            "priority": "high",
        },
    )

    return response


def test_create_task(client):

    token = create_user_and_get_token(
        client
    )

    response = create_task(
        client,
        token
    )

    assert response.status_code == 201

    body = response.json()

    assert body["success"] is True
    assert body["data"]["title"] == "Test Task"
    assert body["data"]["status"] == "todo"
    assert body["data"]["priority"] == "high"


def test_get_task(client):

    token = create_user_and_get_token(
        client
    )

    create_response = create_task(
        client,
        token
    )

    task_id = (
        create_response.json()["data"]["id"]
    )

    response = client.get(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["data"]["id"] == task_id


def test_task_not_found(client):

    token = create_user_and_get_token(
        client
    )

    response = client.get(
        "/tasks/507f1f77bcf86cd799439011",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 404

    body = response.json()

    assert body["success"] is False
    assert body["status_code"] == 404
    assert body["error"] == "NOT_FOUND"


def test_invalid_task_id(client):

    token = create_user_and_get_token(
        client
    )

    response = client.get(
        "/tasks/not-a-valid-object-id",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["success"] is False
    assert body["status_code"] == 400
    assert body["error"] == "BAD_REQUEST"


def test_invalid_task_status(client):

    token = create_user_and_get_token(
        client
    )

    response = client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Invalid Status",
            "description": "Testing invalid status",
            "status": "invalid_status",
            "priority": "high",
        },
    )

    assert response.status_code == 422

    body = response.json()

    assert body["success"] is False
    assert body["status_code"] == 422
    assert body["error"] == "VALIDATION_ERROR"


def test_invalid_task_priority(client):

    token = create_user_and_get_token(
        client
    )

    response = client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Invalid Priority",
            "description": "Testing invalid priority",
            "status": "todo",
            "priority": "urgent",
        },
    )

    assert response.status_code == 422

    body = response.json()

    assert body["success"] is False
    assert body["status_code"] == 422
    assert body["error"] == "VALIDATION_ERROR"


def test_update_task(client):

    token = create_user_and_get_token(
        client
    )

    create_response = create_task(
        client,
        token
    )

    task_id = (
        create_response.json()["data"]["id"]
    )

    response = client.put(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Updated Task",
            "description": "Updated description",
            "status": "in_progress",
            "priority": "medium",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["data"]["title"] == "Updated Task"
    assert body["data"]["status"] == "in_progress"


def test_update_task_status(client):

    token = create_user_and_get_token(
        client
    )

    create_response = create_task(
        client,
        token
    )

    task_id = (
        create_response.json()["data"]["id"]
    )

    response = client.patch(
        f"/tasks/{task_id}/status",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "status": "completed"
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["data"]["status"] == "completed"


def test_delete_task(client):

    token = create_user_and_get_token(
        client
    )

    create_response = create_task(
        client,
        token
    )

    task_id = (
        create_response.json()["data"]["id"]
    )

    response = client.delete(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True


def test_pagination(client):

    token = create_user_and_get_token(
        client
    )

    for i in range(3):

        client.post(
            "/tasks",
            headers={
                "Authorization": f"Bearer {token}"
            },
            json={
                "title": f"Task {i}",
                "description": "Pagination test",
                "status": "todo",
                "priority": "low",
            },
        )

    response = client.get(
        "/tasks?page=1&limit=2",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["page"] == 1
    assert body["limit"] == 2
    assert body["total"] == 3
    assert len(body["data"]) == 2


def test_search(client):

    token = create_user_and_get_token(
        client
    )

    create_response = client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Python Backend Development",
            "description": "Search test",
            "status": "todo",
            "priority": "high",
        },
    )

    assert create_response.status_code == 201

    response = client.get(
        "/tasks?search=Python",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["total"] >= 1


def test_filter_by_status(client):

    token = create_user_and_get_token(
        client
    )

    client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "title": "Completed Task",
            "description": "Filter test",
            "status": "completed",
            "priority": "high",
        },
    )

    response = client.get(
        "/tasks?status=completed",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True

    for task in body["data"]:
        assert task["status"] == "completed"