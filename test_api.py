import pytest
import json
from app import app, db, Todo


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


def make_todo(client, title="Test Todo"):
    return client.post(
        "/api/todos",
        data=json.dumps({"title": title}),
        content_type="application/json"
    )


class TestGetAllTodos:
    def test_get_todos_empty(self, client):
        db.session.query(Todo).delete()
        db.session.commit()
        response = client.get("/api/todos")
        assert response.status_code == 200
        assert response.get_json() == []

    def test_get_todos_with_items(self, client):
        make_todo(client, "Buy milk")
        make_todo(client, "Walk the dog")
        response = client.get("/api/todos")
        assert response.status_code == 200
        assert len(response.get_json()) == 2

    def test_get_todos_correct_fields(self, client):
        make_todo(client, "Check fields")
        todo = client.get("/api/todos").get_json()[0]
        assert "id" in todo
        assert "title" in todo
        assert "complete" in todo


class TestGetOneTodo:
    def test_get_existing_todo(self, client):
        created = make_todo(client, "Read a book").get_json()
        response = client.get(f"/api/todos/{created['id']}")
        assert response.status_code == 200
        assert response.get_json()["title"] == "Read a book"

    def test_get_nonexistent_todo(self, client):
        response = client.get("/api/todos/9999")
        assert response.status_code == 404
        assert "error" in response.get_json()


class TestCreateTodo:
    def test_create_todo(self, client):
        response = make_todo(client, "Go for a run")
        assert response.status_code == 201
        assert response.get_json()["title"] == "Go for a run"

    def test_create_todo_missing_title(self, client):
        response = client.post(
            "/api/todos",
            data=json.dumps({}),
            content_type="application/json"
        )
        assert response.status_code == 400

    def test_create_todo_empty_title(self, client):
        response = client.post(
            "/api/todos",
            data=json.dumps({"title": "   "}),
            content_type="application/json"
        )
        assert response.status_code == 400

    def test_create_todo_no_body(self, client):
        response = client.post("/api/todos", content_type="application/json")
        assert response.status_code == 400


class TestUpdateTodo:
    def test_update_title(self, client):
        created = make_todo(client, "Old title").get_json()
        response = client.put(
            f"/api/todos/{created['id']}",
            data=json.dumps({"title": "New title"}),
            content_type="application/json"
        )
        assert response.status_code == 200
        assert response.get_json()["title"] == "New title"

    def test_update_complete(self, client):
        created = make_todo(client, "Finish homework").get_json()
        response = client.put(
            f"/api/todos/{created['id']}",
            data=json.dumps({"complete": True}),
            content_type="application/json"
        )
        assert response.status_code == 200
        assert response.get_json()["complete"] is True

    def test_update_nonexistent(self, client):
        response = client.put(
            "/api/todos/9999",
            data=json.dumps({"title": "Ghost"}),
            content_type="application/json"
        )
        assert response.status_code == 404

    def test_update_no_body(self, client):
        created = make_todo(client, "Some todo").get_json()
        response = client.put(
            f"/api/todos/{created['id']}",
            content_type="application/json"
        )
        assert response.status_code == 400

    def test_update_empty_title(self, client):
        created = make_todo(client, "Valid todo").get_json()
        response = client.put(
            f"/api/todos/{created['id']}",
            data=json.dumps({"title": ""}),
            content_type="application/json"
        )
        assert response.status_code == 400

    def test_update_wrong_complete_type(self, client):
        created = make_todo(client, "Type test").get_json()
        response = client.put(
            f"/api/todos/{created['id']}",
            data=json.dumps({"complete": "yes"}),
            content_type="application/json"
        )
        assert response.status_code == 400


class TestDeleteTodo:
    def test_delete_todo(self, client):
        created = make_todo(client, "Delete me").get_json()
        response = client.delete(f"/api/todos/{created['id']}")
        assert response.status_code == 200
        assert "deleted" in response.get_json()["message"].lower()

    def test_deleted_todo_gone(self, client):
        created = make_todo(client, "Temporary").get_json()
        client.delete(f"/api/todos/{created['id']}")
        response = client.get(f"/api/todos/{created['id']}")
        assert response.status_code == 404

    def test_delete_nonexistent(self, client):
        response = client.delete("/api/todos/9999")
        assert response.status_code == 404