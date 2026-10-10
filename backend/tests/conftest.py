import os
import tempfile

# Configure before the app is imported: settings and the DB engine are created at import time.
os.environ.update(
    YUI_DATA_DIR=tempfile.mkdtemp(prefix="yui-test-"),
    YUI_ENGINE="mock",
    YUI_AUTO_UPDATE="false",
)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def app_instance():
    with TestClient(app):  # runs the lifespan once (DB init + worker)
        yield app


@pytest.fixture
def client_factory(app_instance):
    """Each client has its own cookie jar, i.e. its own logged-in user."""

    def make(username: str, password: str = "password123") -> TestClient:
        client = TestClient(app_instance)
        response = client.post("/api/auth/register", json={"username": username, "password": password})
        if response.status_code == 409:
            client.post("/api/auth/login", json={"username": username, "password": password})
        return client

    return make
