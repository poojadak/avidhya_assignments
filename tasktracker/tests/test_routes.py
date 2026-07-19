import pytest
from app import create_app, tasks


@pytest.fixture(autouse=True)
def clear_tasks():
    tasks.clear()
    yield
    tasks.clear()


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def _create(client, title="Buy milk", status="todo"):
    return client.post("/tasks", json={"title": title, "status": status})


class TestDeleteTask:
    def test_delete_existing_task_returns_204(self, client):
        task_id = _create(client).get_json()["id"]
        res = client.delete(f"/tasks/{task_id}")
        assert res.status_code == 204
        assert res.data == b""

    def test_deleted_task_no_longer_retrievable(self, client):
        task_id = _create(client).get_json()["id"]
        client.delete(f"/tasks/{task_id}")
        assert client.get(f"/tasks/{task_id}").status_code == 404

    def test_delete_nonexistent_task_returns_404(self, client):
        res = client.delete("/tasks/nonexistent-id")
        assert res.status_code == 404
        assert res.get_json() == {"error": "task not found"}

    def test_delete_removes_task_from_list(self, client):
        task_id = _create(client).get_json()["id"]
        client.delete(f"/tasks/{task_id}")
        ids = [t["id"] for t in client.get("/tasks").get_json()]
        assert task_id not in ids
