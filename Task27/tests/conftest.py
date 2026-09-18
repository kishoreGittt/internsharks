import pytest

from fastapi.testclient import TestClient

from app.main import app

from app.auth.dependencies import (
    get_current_user
)


@pytest.fixture
def client():

    return TestClient(
        app
    )


@pytest.fixture
def authenticated_client():

    async def fake_user():

        return {
            "user_id":
                "test-user-001",

            "email":
                "test@example.com"
        }

    app.dependency_overrides[
        get_current_user
    ] = fake_user

    client = TestClient(
        app
    )

    yield client

    app.dependency_overrides.clear()