import pytest
from app import app, db, Todo


@pytest.fixture
def client():
    """
    Configure the app for testing:
    - Uses an in-memory SQLite database (never touches your real db.sqlite)
    - Creates all tables before each test
    - Drops all tables after each test
    """
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


# ─────────────────────────────────────────
# Helper
# ─────────────────────────────────────────

def create_todo(client, title="Test Todo"):
    """Helper to create a todo via the API and return the response."""
    return client.post(
        "/api/todos",
        json={"title": title},
        content_type="application/json"
    )


# ─────────────────────────────────────────
# GET /api/todos  (Read All)
# ─────────────────────────────────────────

def test_get_all_todos_empty(client):
    """GET all todos returns empty list when no todos exist."""
    response = client.get("/api/todos")
    assert response.status_code == 200
    assert response.get_json() == []


def test_get_all_todos_with_data(client):
    """GET all todos returns all created todos."""
    create_todo(client, "First")
    create_todo(client, "Second")
    response = client.get("/api/todos")
    data = response.get_json()
    assert response.status_code == 200
    assert len(data) == 2
    titles = [item["title"] for item in data]
    assert "First" in titles
    assert "Second" in titles


# ─────────────────────────────────────────
# GET /api/todos/<id>  (Read One)
# ─────────────────────────────────────────

def test_get_single_todo_success(client):
    """GET a single todo returns the correct item."""
    created = create_todo(client, "Single Todo").get_json()
    todo_id = created["id"]

    response = client.get(f"/api/todos/{todo_id}")
    data = response.get_json()
    assert response.status_code == 200
    assert data["id"] == todo_id
    assert data["title"] == "Single Todo"
    assert data["complete"] is False


def test_get_single_todo_not_found(client):
    """GET a non-existent todo returns 404."""
    response = client.get("/api/todos/9999")
    assert response.status_code == 404
    assert "error" in response.get_json()


# ─────────────────────────────────────────
# POST /api/todos  (Create)
# ─────────────────────────────────────────

def test_create_todo_success(client):
    """POST creates a new todo and returns 201."""
    response = create_todo(client, "Buy groceries")
    data = response.get_json()
    assert response.status_code == 201
    assert data["title"] == "Buy groceries"
    assert data["complete"] is False
    assert "id" in data


def test_create_todo_missing_title(client):
    """POST without title returns 400."""
    response = client.post(
        "/api/todos",
        json={},
        content_type="application/json"
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_todo_empty_title(client):
    """POST with empty title string returns 400."""
    response = client.post(
        "/api/todos",
        json={"title": "   "},
        content_type="application/json" # pragma: no cover
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_todo_no_json_body(client):
    """POST with no JSON body at all returns 400."""
    response = client.post("/api/todos", content_type="application/json")
    assert response.status_code == 400


# ─────────────────────────────────────────
# PUT /api/todos/<id>  (Update)
# ─────────────────────────────────────────

def test_update_todo_title(client):
    """PUT updates the title of a todo."""
    todo_id = create_todo(client, "Old Title").get_json()["id"]

    response = client.put(
        f"/api/todos/{todo_id}",
        json={"title": "New Title"},
        content_type="application/json"
    )
    data = response.get_json()
    assert response.status_code == 200
    assert data["title"] == "New Title"


def test_update_todo_complete_status(client):
    """PUT updates the complete status of a todo."""
    todo_id = create_todo(client).get_json()["id"]

    response = client.put(
        f"/api/todos/{todo_id}",
        json={"complete": True},
        content_type="application/json"
    )
    data = response.get_json()
    assert response.status_code == 200
    assert data["complete"] is True


def test_update_todo_both_fields(client):
    """PUT can update both title and complete at the same time."""
    todo_id = create_todo(client, "Old").get_json()["id"]

    response = client.put(
        f"/api/todos/{todo_id}",
        json={"title": "Updated", "complete": True},
        content_type="application/json"
    )
    data = response.get_json()
    assert response.status_code == 200
    assert data["title"] == "Updated"
    assert data["complete"] is True


def test_update_todo_not_found(client):
    """PUT on a non-existent ID returns 404."""
    response = client.put(
        "/api/todos/9999",
        json={"title": "Doesn't matter"},
        content_type="application/json"
    )
    assert response.status_code == 404
    assert "error" in response.get_json()


def test_update_todo_empty_title(client):
    """PUT with empty title returns 400."""
    todo_id = create_todo(client).get_json()["id"]

    response = client.put(
        f"/api/todos/{todo_id}",
        json={"title": ""},
        content_type="application/json"
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_update_todo_invalid_complete_type(client):
    """PUT with non-boolean complete value returns 400."""
    todo_id = create_todo(client).get_json()["id"]

    response = client.put(
        f"/api/todos/{todo_id}",
        json={"complete": "yes"},
        content_type="application/json"
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_update_todo_no_data(client):
    """PUT with no JSON body returns 400."""
    todo_id = create_todo(client).get_json()["id"]

    response = client.put(
        f"/api/todos/{todo_id}",
        content_type="application/json"
    )
    assert response.status_code == 400


# ─────────────────────────────────────────
# DELETE /api/todos/<id>  (Delete)
# ─────────────────────────────────────────

def test_delete_todo_success(client):
    """DELETE removes a todo and returns success message."""
    todo_id = create_todo(client).get_json()["id"]

    response = client.delete(f"/api/todos/{todo_id}")
    assert response.status_code == 200
    assert "message" in response.get_json()


def test_delete_todo_actually_removed(client):
    """After DELETE, the todo can no longer be fetched."""
    todo_id = create_todo(client).get_json()["id"]
    client.delete(f"/api/todos/{todo_id}")

    response = client.get(f"/api/todos/{todo_id}")
    assert response.status_code == 404


def test_delete_todo_not_found(client):
    """DELETE on a non-existent ID returns 404."""
    response = client.delete("/api/todos/9999")
    assert response.status_code == 404
    assert "error" in response.get_json()


# ─────────────────────────────────────────
# Legacy HTML routes (coverage completion)
# ─────────────────────────────────────────

def test_home_page(client):
    """GET / returns 200 and renders the home page."""
    response = client.get("/")
    assert response.status_code == 200


def test_add_todo_form(client):
    """POST /add creates a todo and redirects."""
    response = client.post("/add", data={"title": "Form Todo"})
    assert response.status_code == 302


def test_update_todo_form(client):
    """GET /update/<id> toggles complete and redirects."""
    todo_id = create_todo(client).get_json()["id"]
    response = client.get(f"/update/{todo_id}")
    assert response.status_code == 302


def test_delete_todo_form(client):
    """GET /delete/<id> removes todo and redirects."""
    todo_id = create_todo(client).get_json()["id"]
    response = client.get(f"/delete/{todo_id}")
    assert response.status_code == 302