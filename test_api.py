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


# Helper

def create_todo(client, title="Test Todo", description=None, due_date=None, priority=None):
    """Helper to create a todo via the API and return the response."""
    payload = {"title": title}
    if description is not None:
        payload["description"] = description
    if due_date is not None:
        payload["due_date"] = due_date
    if priority is not None:
        payload["priority"] = priority
    return client.post("/api/todos", json=payload, content_type="application/json")


# GET /api/todos  (Read All)

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


# GET /api/todos/<id> (Only One)

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


# POST /api/todos  (Create)

def test_create_todo_success(client):
    """POST creates a basic todo and returns 201."""
    response = create_todo(client, "Buy groceries")
    data = response.get_json()
    assert response.status_code == 201
    assert data["title"] == "Buy groceries"
    assert data["complete"] is False
    assert data["description"] is None
    assert data["due_date"] is None
    assert data["priority"] is None
    assert "id" in data


def test_create_todo_with_all_fields(client):
    """POST creates a todo with description, due_date, and priority."""
    response = create_todo(
        client,
        title="Full Todo",
        description="This is a description",
        due_date="2026-12-31",
        priority="high"
    )
    data = response.get_json()
    assert response.status_code == 201
    assert data["title"] == "Full Todo"
    assert data["description"] == "This is a description"
    assert data["due_date"] == "2026-12-31"
    assert data["priority"] == "high"


def test_create_todo_with_description(client):
    """POST creates a todo with a description."""
    response = create_todo(client, title="With Desc", description="Some details")
    data = response.get_json()
    assert response.status_code == 201
    assert data["description"] == "Some details"


def test_create_todo_with_due_date(client):
    """POST creates a todo with a due date."""
    response = create_todo(client, title="With Date", due_date="2026-06-30")
    data = response.get_json()
    assert response.status_code == 201
    assert data["due_date"] == "2026-06-30"


def test_create_todo_with_priority_low(client):
    """POST creates a todo with low priority."""
    response = create_todo(client, title="Low", priority="low")
    assert response.status_code == 201
    assert response.get_json()["priority"] == "low"


def test_create_todo_with_priority_medium(client):
    """POST creates a todo with medium priority."""
    response = create_todo(client, title="Medium", priority="medium")
    assert response.status_code == 201
    assert response.get_json()["priority"] == "medium"


def test_create_todo_with_priority_high(client):
    """POST creates a todo with high priority."""
    response = create_todo(client, title="High", priority="high")
    assert response.status_code == 201
    assert response.get_json()["priority"] == "high"


def test_create_todo_missing_title(client):
    """POST without title returns 400."""
    response = client.post("/api/todos", json={}, content_type="application/json")
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_todo_empty_title(client):
    """POST with empty title string returns 400."""
    response = client.post(
        "/api/todos",
        json={"title": "   "},
        content_type="application/json"
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_todo_no_json_body(client):
    """POST with no JSON body at all returns 400."""
    response = client.post("/api/todos", content_type="application/json")
    assert response.status_code == 400


def test_create_todo_invalid_due_date(client):
    """POST with invalid due_date format returns 400."""
    response = client.post(
        "/api/todos",
        json={"title": "Test", "due_date": "31-12-2026"},
        content_type="application/json"
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_todo_invalid_priority(client):
    """POST with invalid priority value returns 400."""
    response = client.post(
        "/api/todos",
        json={"title": "Test", "priority": "urgent"},
        content_type="application/json"
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


# PUT /api/todos/<id>  (Update)

def test_update_todo_title(client):
    """PUT updates the title of a todo."""
    todo_id = create_todo(client, "Old Title").get_json()["id"]
    response = client.put(
        f"/api/todos/{todo_id}",
        json={"title": "New Title"},
        content_type="application/json"
    )
    assert response.status_code == 200
    assert response.get_json()["title"] == "New Title"


def test_update_todo_complete_status(client):
    """PUT updates the complete status of a todo."""
    todo_id = create_todo(client).get_json()["id"]
    response = client.put(
        f"/api/todos/{todo_id}",
        json={"complete": True},
        content_type="application/json"
    )
    assert response.status_code == 200
    assert response.get_json()["complete"] is True


def test_update_todo_description(client):
    """PUT updates the description of a todo."""
    todo_id = create_todo(client).get_json()["id"]
    response = client.put(
        f"/api/todos/{todo_id}",
        json={"description": "Updated description"},
        content_type="application/json"
    )
    assert response.status_code == 200
    assert response.get_json()["description"] == "Updated description"


def test_update_todo_description_to_null(client):
    """PUT can clear a description by setting it to null."""
    todo_id = create_todo(client, description="Has desc").get_json()["id"]
    response = client.put(
        f"/api/todos/{todo_id}",
        json={"description": None},
        content_type="application/json"
    )
    assert response.status_code == 200
    assert response.get_json()["description"] is None


def test_update_todo_due_date(client):
    """PUT updates the due date of a todo."""
    todo_id = create_todo(client).get_json()["id"]
    response = client.put(
        f"/api/todos/{todo_id}",
        json={"due_date": "2026-12-01"},
        content_type="application/json"
    )
    assert response.status_code == 200
    assert response.get_json()["due_date"] == "2026-12-01"


def test_update_todo_due_date_to_null(client):
    """PUT can clear a due date by setting it to null."""
    todo_id = create_todo(client, due_date="2026-12-01").get_json()["id"]
    response = client.put(
        f"/api/todos/{todo_id}",
        json={"due_date": None},
        content_type="application/json"
    )
    assert response.status_code == 200
    assert response.get_json()["due_date"] is None


def test_update_todo_priority(client):
    """PUT updates the priority of a todo."""
    todo_id = create_todo(client).get_json()["id"]
    response = client.put(
        f"/api/todos/{todo_id}",
        json={"priority": "medium"},
        content_type="application/json"
    )
    assert response.status_code == 200
    assert response.get_json()["priority"] == "medium"


def test_update_todo_priority_to_null(client):
    """PUT can clear priority by setting it to null."""
    todo_id = create_todo(client, priority="high").get_json()["id"]
    response = client.put(
        f"/api/todos/{todo_id}",
        json={"priority": None},
        content_type="application/json"
    )
    assert response.status_code == 200
    assert response.get_json()["priority"] is None


def test_update_todo_all_fields(client):
    """PUT can update all fields at once."""
    todo_id = create_todo(client, "Old").get_json()["id"]
    response = client.put(
        f"/api/todos/{todo_id}",
        json={
            "title": "Updated",
            "complete": True,
            "description": "New desc",
            "due_date": "2026-11-01",
            "priority": "low"
        },
        content_type="application/json"
    )
    data = response.get_json()
    assert response.status_code == 200
    assert data["title"] == "Updated"
    assert data["complete"] is True
    assert data["description"] == "New desc"
    assert data["due_date"] == "2026-11-01"
    assert data["priority"] == "low"


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


def test_update_todo_invalid_due_date(client):
    """PUT with invalid due_date format returns 400."""
    todo_id = create_todo(client).get_json()["id"]
    response = client.put(
        f"/api/todos/{todo_id}",
        json={"due_date": "not-a-date"},
        content_type="application/json"
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_update_todo_invalid_priority(client):
    """PUT with invalid priority value returns 400."""
    todo_id = create_todo(client).get_json()["id"]
    response = client.put(
        f"/api/todos/{todo_id}",
        json={"priority": "critical"},
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


# DELETE /api/todos/<id>  (Delete)

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


# Legacy HTML routes (coverage completion)

def test_home_page(client):
    """GET / returns 200 and renders the home page."""
    response = client.get("/")
    assert response.status_code == 200


def test_add_todo_form(client):
    """POST /add with all fields creates a todo and redirects."""
    response = client.post("/add", data={
        "title": "Form Todo",
        "description": "A description",
        "due_date": "2026-12-31",
        "priority": "high"
    })
    assert response.status_code == 302


def test_add_todo_form_minimal(client):
    """POST /add with only title creates a todo and redirects."""
    response = client.post("/add", data={"title": "Minimal Todo"})
    assert response.status_code == 302


def test_add_todo_form_invalid_date(client):
    """POST /add with a bad date string still redirects (graceful fallback)."""
    response = client.post("/add", data={
        "title": "Bad Date Todo",
        "due_date": "not-a-date"
    })
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