"""API tests for the Task Tracker.

Each test is linked to a specification in the knowledge database.
"""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestCreateTask:
    """SPEC-001: Users can create tasks with title and description."""

    def test_create_returns_201(self, client: TestClient):
        """TEST-001: POST /tasks returns 201."""
        resp = client.post("/tasks", json={"title": "Buy groceries"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Buy groceries"
        assert data["id"].startswith("TASK-")
        assert data["status"] == "created"

    def test_create_without_title_returns_422(self, client: TestClient):
        """TEST-002: POST /tasks with no title returns error."""
        resp = client.post("/tasks", json={})
        assert resp.status_code == 422


class TestStatusTransitions:
    """SPEC-002: Tasks transition through created → in_progress → done."""

    def test_invalid_transition_returns_400(self, client: TestClient):
        """TEST-003: Invalid status transition returns 400."""
        resp = client.post("/tasks", json={"title": "Test"})
        task_id = resp.json()["id"]
        # Cannot go directly from created to done
        resp = client.patch(f"/tasks/{task_id}", json={"status": "done"})
        assert resp.status_code == 400

    def test_valid_transition_succeeds(self, client: TestClient):
        """TEST-004: Valid transition created → in_progress succeeds."""
        resp = client.post("/tasks", json={"title": "Test"})
        task_id = resp.json()["id"]
        resp = client.patch(f"/tasks/{task_id}", json={"status": "in_progress"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "in_progress"


class TestAssignment:
    """SPEC-003: Tasks can be assigned to a user."""

    def test_assignee_stored(self, client: TestClient):
        """TEST-005: PATCH with assignee stores user ID."""
        resp = client.post("/tasks", json={"title": "Test"})
        task_id = resp.json()["id"]
        resp = client.patch(f"/tasks/{task_id}", json={"assignee": "alice"})
        assert resp.status_code == 200
        assert resp.json()["assignee"] == "alice"


class TestListOrder:
    """SPEC-004: Task list returns results in creation order."""

    def test_list_order(self, client: TestClient):
        """TEST-006: GET /tasks returns tasks in creation order."""
        client.post("/tasks", json={"title": "First"})
        client.post("/tasks", json={"title": "Second"})
        client.post("/tasks", json={"title": "Third"})
        resp = client.get("/tasks")
        titles = [t["title"] for t in resp.json()]
        assert titles == ["First", "Second", "Third"]


class TestDelete:
    """SPEC-005: Deleted tasks return 404 on subsequent GET."""

    def test_delete_then_get_returns_404(self, client: TestClient):
        """TEST-007: DELETE then GET returns 404."""
        resp = client.post("/tasks", json={"title": "Doomed"})
        task_id = resp.json()["id"]
        resp = client.delete(f"/tasks/{task_id}")
        assert resp.status_code == 204
        resp = client.get(f"/tasks/{task_id}")
        assert resp.status_code == 404
