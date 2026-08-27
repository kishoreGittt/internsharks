import os

import pytest
from fastapi.testclient import TestClient

os.environ["APP_ENV"] = "testing"

from app.main import app
from app.database.mongodb import (
    tasks_collection,
    users_collection,
    refresh_tokens_collection,
)


@pytest.fixture
def client():

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
async def clean_database():

    await users_collection.delete_many({})
    await tasks_collection.delete_many({})
    await refresh_tokens_collection.delete_many({})

    yield

    await users_collection.delete_many({})
    await tasks_collection.delete_many({})
    await refresh_tokens_collection.delete_many({})