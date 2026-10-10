import time


def wait_for_song(client, song_id: int, timeout: float = 30) -> dict:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        song = client.get(f"/api/songs/{song_id}").json()
        if song["status"] in ("succeeded", "failed"):
            return song
        time.sleep(0.2)
    raise AssertionError("song did not finish in time")


def test_projects_are_isolated_between_users(client_factory):
    owner = client_factory("owner")
    intruder = client_factory("intruder")
    project = owner.post("/api/projects", json={"name": "Album"}).json()

    assert intruder.get(f"/api/projects/{project['id']}").status_code == 404
    assert intruder.get("/api/projects").json() == []
    assert intruder.post("/api/songs", json={"style": "pop", "project_id": project["id"]}).status_code == 404


def test_generate_song_end_to_end(client_factory):
    client = client_factory("musician")
    project = client.post("/api/projects", json={"name": "Demo"}).json()
    created = client.post(
        "/api/songs",
        json={"title": "Test", "style": "piano pop, 88 BPM", "lyrics": "[Verse]\nla la", "variants": 2,
              "seed": 10, "project_id": project["id"]},
    )
    assert created.status_code == 201
    first, second = created.json()
    assert (first["seed"], second["seed"]) == (10, 11)

    song = wait_for_song(client, first["id"])
    assert song["status"] == "succeeded"
    assert song["has_audio"] and song["has_score"]
    assert client.get(f"/api/songs/{song['id']}/audio").content[:4] == b"RIFF"
    assert "X:1" in client.get(f"/api/songs/{song['id']}/score").text

    assert len(client.get("/api/songs", params={"project_id": project["id"]}).json()) == 2
    client.patch(f"/api/songs/{song['id']}", json={"is_favorite": True})
    assert [s["id"] for s in client.get("/api/songs", params={"is_favorite": True}).json()] == [song["id"]]

    wait_for_song(client, second["id"])
    assert client.delete(f"/api/songs/{second['id']}").status_code == 204
    assert client.get(f"/api/songs/{second['id']}").status_code == 404


def test_abc_requires_a_plan(client_factory):
    client = client_factory("composer")
    response = client.post("/api/songs", json={"style": "jazz", "abc": "X:1", "plan_mode": "off"})
    assert response.status_code == 422
