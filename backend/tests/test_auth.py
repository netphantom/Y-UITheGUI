def test_first_user_is_admin_and_logout_revokes_session(client_factory):
    client = client_factory("alice")
    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["is_admin"] is True

    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/auth/me").status_code == 401


def test_wrong_password_is_rejected(client_factory):
    client_factory("bob")
    other = client_factory("carol")
    other.post("/api/auth/logout")
    response = other.post("/api/auth/login", json={"username": "bob", "password": "wrong-password"})
    assert response.status_code == 401


def test_non_admin_cannot_list_users(client_factory):
    client = client_factory("dave")
    assert client.get("/api/auth/users").status_code == 403


def test_system_status_is_public(app_instance):
    from fastapi.testclient import TestClient

    status = TestClient(app_instance).get("/api/system/status").json()
    assert status["engine"] == "mock"
    assert status["engine_ready"] is True
    assert status["engine_error"] is None
