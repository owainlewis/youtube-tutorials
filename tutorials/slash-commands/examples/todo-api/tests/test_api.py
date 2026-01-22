"""Tests for the Todo API."""

import os
import pytest
from fastapi.testclient import TestClient

# Use a test database
os.environ["DATABASE"] = "test_todos.db"

from main import app, DATABASE, init_db, get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create a fresh database for each test."""
    # Remove existing test database
    if os.path.exists(DATABASE):
        os.remove(DATABASE)

    init_db()
    yield

    # Cleanup
    if os.path.exists(DATABASE):
        os.remove(DATABASE)


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestCreateTodo:
    """Tests for POST /todos."""

    def test_create_todo_with_title(self, client):
        """Create a todo with just a title."""
        response = client.post("/todos", json={"title": "Buy groceries"})

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Buy groceries"
        assert data["description"] is None
        assert data["completed"] is False
        assert data["id"] is not None

    def test_create_todo_with_description(self, client):
        """Create a todo with title and description."""
        response = client.post(
            "/todos",
            json={"title": "Buy groceries", "description": "Milk, eggs, bread"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Buy groceries"
        assert data["description"] == "Milk, eggs, bread"

    def test_create_todo_without_title_fails(self, client):
        """Creating a todo without a title should fail."""
        response = client.post("/todos", json={"description": "Missing title"})

        assert response.status_code == 422


class TestListTodos:
    """Tests for GET /todos."""

    def test_list_empty(self, client):
        """List todos when none exist."""
        response = client.get("/todos")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_multiple_todos(self, client):
        """List multiple todos."""
        client.post("/todos", json={"title": "First"})
        client.post("/todos", json={"title": "Second"})

        response = client.get("/todos")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


class TestGetTodo:
    """Tests for GET /todos/{id}."""

    def test_get_existing_todo(self, client):
        """Get a todo that exists."""
        create_response = client.post("/todos", json={"title": "Test todo"})
        todo_id = create_response.json()["id"]

        response = client.get(f"/todos/{todo_id}")

        assert response.status_code == 200
        assert response.json()["title"] == "Test todo"

    def test_get_nonexistent_todo(self, client):
        """Get a todo that doesn't exist."""
        response = client.get("/todos/999")

        assert response.status_code == 404


class TestUpdateTodo:
    """Tests for PATCH /todos/{id}."""

    def test_update_title(self, client):
        """Update a todo's title."""
        create_response = client.post("/todos", json={"title": "Original"})
        todo_id = create_response.json()["id"]

        response = client.patch(f"/todos/{todo_id}", json={"title": "Updated"})

        assert response.status_code == 200
        assert response.json()["title"] == "Updated"

    def test_mark_complete(self, client):
        """Mark a todo as complete."""
        create_response = client.post("/todos", json={"title": "Test"})
        todo_id = create_response.json()["id"]

        response = client.patch(f"/todos/{todo_id}", json={"completed": True})

        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is True
        assert data["completed_at"] is not None

    def test_mark_incomplete_clears_timestamp(self, client):
        """Marking a todo incomplete should clear completed_at."""
        create_response = client.post("/todos", json={"title": "Test"})
        todo_id = create_response.json()["id"]

        # Complete it
        client.patch(f"/todos/{todo_id}", json={"completed": True})

        # Uncomplete it
        response = client.patch(f"/todos/{todo_id}", json={"completed": False})

        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is False
        assert data["completed_at"] is None

    def test_update_nonexistent_todo(self, client):
        """Update a todo that doesn't exist."""
        response = client.patch("/todos/999", json={"title": "Won't work"})

        assert response.status_code == 404


class TestDeleteTodo:
    """Tests for DELETE /todos/{id}."""

    def test_delete_existing_todo(self, client):
        """Delete a todo that exists."""
        create_response = client.post("/todos", json={"title": "To delete"})
        todo_id = create_response.json()["id"]

        response = client.delete(f"/todos/{todo_id}")

        assert response.status_code == 204

        # Verify it's gone
        get_response = client.get(f"/todos/{todo_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_todo(self, client):
        """Delete a todo that doesn't exist."""
        response = client.delete("/todos/999")

        assert response.status_code == 404
