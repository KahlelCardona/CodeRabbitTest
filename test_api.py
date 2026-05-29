# ─────────────────────────────────────────────
# test_api.py — Tests for the Flask Todo REST API
# ─────────────────────────────────────────────

import pytest
from app import app, db, Todo

# ─────────────────────────────────────────────
# SETUP — runs before and after each test
# ─────────────────────────────────────────────

@pytest.fixture
def client():
    """
    This is a pytest fixture. Think of it as a "setup function."
    It runs before each test to give us a fresh, clean app and database.
    """
    # Tell Flask to use a separate in-memory database for testing
    # (so we don't mess up the real database)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()       # Create fresh tables
        yield app.test_client()  # Give the test a "fake browser" to send requests
        db.drop_all()         # Delete everything after the test is done


# ─────────────────────────────────────────────
# HELPER FUNCTION
# ─────────────────────────────────────────────

def create_task(client, title="Test Task", complete=False):
    """Helper that creates a task and returns the response. 
    Avoids repeating the same code in every test."""
    return client.post('/api/tasks',
                       json={'title': title, 'complete': complete},
                       content_type='application/json')


# ═══════════════════════════════════════════════
# CREATE TESTS (POST /api/tasks)
# ═══════════════════════════════════════════════

def test_create_task_success(client):
    """POSITIVE: Create a task with valid data — should succeed"""
    response = create_task(client, title="Buy groceries")
    data = response.get_json()

    # Check that the HTTP status code is 201 (Created)
    assert response.status_code == 201

    # Check that the response contains the right data
    assert data['title'] == 'Buy groceries'
    assert data['complete'] == False
    assert 'id' in data  # An ID should have been assigned


def test_create_task_with_complete_true(client):
    """POSITIVE: Create a task that is already marked as complete"""
    response = create_task(client, title="Done task", complete=True)
    data = response.get_json()

    assert response.status_code == 201
    assert data['complete'] == True


def test_create_task_missing_title(client):
    """NEGATIVE: Try to create a task without a title — should fail"""
    response = client.post('/api/tasks',
                           json={'complete': False},
                           content_type='application/json')
    data = response.get_json()

    assert response.status_code == 400
    assert 'error' in data
    assert data['error'] == 'Title is required'


def test_create_task_empty_title(client):
    """NEGATIVE: Try to create a task with an empty title string"""
    response = client.post('/api/tasks',
                           json={'title': '   '},  # Only spaces
                           content_type='application/json')
    data = response.get_json()

    assert response.status_code == 400
    assert data['error'] == 'Title is required'


def test_create_task_no_body(client):
    """NEGATIVE: Send a POST with no body at all"""
    response = client.post('/api/tasks',
                           content_type='application/json')
    data = response.get_json()

    assert response.status_code == 400


# ═══════════════════════════════════════════════
# READ ALL TESTS (GET /api/tasks)
# ═══════════════════════════════════════════════

def test_get_all_tasks_empty(client):
    """POSITIVE: Get all tasks when database is empty"""
    response = client.get('/api/tasks')
    data = response.get_json()

    assert response.status_code == 200
    assert data == []  # Should be an empty list


def test_get_all_tasks_with_data(client):
    """POSITIVE: Get all tasks after creating some"""
    create_task(client, title="Task 1")
    create_task(client, title="Task 2")

    response = client.get('/api/tasks')
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]['title'] == 'Task 1'
    assert data[1]['title'] == 'Task 2'


# ═══════════════════════════════════════════════
# READ ONE TESTS (GET /api/tasks/<id>)
# ═══════════════════════════════════════════════

def test_get_task_success(client):
    """POSITIVE: Get a task that exists"""
    create_response = create_task(client, title="Single Task")
    task_id = create_response.get_json()['id']

    response = client.get(f'/api/tasks/{task_id}')
    data = response.get_json()

    assert response.status_code == 200
    assert data['title'] == 'Single Task'
    assert data['id'] == task_id


def test_get_task_not_found(client):
    """NEGATIVE: Try to get a task that doesn't exist"""
    response = client.get('/api/tasks/9999')
    data = response.get_json()

    assert response.status_code == 404
    assert data['error'] == 'Task not found'


# ═══════════════════════════════════════════════
# UPDATE TESTS (PUT /api/tasks/<id>)
# ═══════════════════════════════════════════════

def test_update_task_title(client):
    """POSITIVE: Update the title of an existing task"""
    task_id = create_task(client, title="Old Title").get_json()['id']

    response = client.put(f'/api/tasks/{task_id}',
                          json={'title': 'New Title'},
                          content_type='application/json')
    data = response.get_json()

    assert response.status_code == 200
    assert data['title'] == 'New Title'


def test_update_task_complete_status(client):
    """POSITIVE: Mark a task as complete"""
    task_id = create_task(client, title="Finish homework").get_json()['id']

    response = client.put(f'/api/tasks/{task_id}',
                          json={'complete': True},
                          content_type='application/json')
    data = response.get_json()

    assert response.status_code == 200
    assert data['complete'] == True


def test_update_task_not_found(client):
    """NEGATIVE: Try to update a task that doesn't exist"""
    response = client.put('/api/tasks/9999',
                          json={'title': 'Ghost Task'},
                          content_type='application/json')
    data = response.get_json()

    assert response.status_code == 404
    assert data['error'] == 'Task not found'


def test_update_task_empty_body(client):
    """NEGATIVE: Try to update with no body"""
    task_id = create_task(client).get_json()['id']

    response = client.put(f'/api/tasks/{task_id}',
                          content_type='application/json')
    data = response.get_json()

    assert response.status_code == 400


def test_update_task_empty_title(client):
    """NEGATIVE: Try to update title with empty string"""
    task_id = create_task(client, title="Valid Task").get_json()['id']

    response = client.put(f'/api/tasks/{task_id}',
                          json={'title': ''},
                          content_type='application/json')
    data = response.get_json()

    assert response.status_code == 400
    assert data['error'] == 'Title cannot be empty'


# ═══════════════════════════════════════════════
# DELETE TESTS (DELETE /api/tasks/<id>)
# ═══════════════════════════════════════════════

def test_delete_task_success(client):
    """POSITIVE: Delete a task that exists"""
    task_id = create_task(client, title="To be deleted").get_json()['id']

    response = client.delete(f'/api/tasks/{task_id}')
    data = response.get_json()

    assert response.status_code == 200
    assert data['message'] == 'Task deleted successfully'

    # Verify the task is really gone
    get_response = client.get(f'/api/tasks/{task_id}')
    assert get_response.status_code == 404


def test_delete_task_not_found(client):
    """NEGATIVE: Try to delete a task that doesn't exist"""
    response = client.delete('/api/tasks/9999')
    data = response.get_json()

    assert response.status_code == 404
    assert data['error'] == 'Task not found'