# Flask Todo REST API

> Extended version of [patrickloeber/flask-todo](https://github.com/patrickloeber/flask-todo) with a full REST API for task management.

## Original Project

This project is built on top of the [Simple Flask Todo App](https://github.com/patrickloeber/flask-todo) by Patrick Loeber. The original app provides a web interface for managing todo tasks.

## New Feature: REST API for Tasks

I added a complete REST API that allows external applications to manage tasks programmatically using JSON. This extends the original app's purpose by making task data accessible to any client (mobile apps, other servers, tools like Postman).

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | Get all tasks |
| GET | `/api/tasks/<id>` | Get a specific task |
| POST | `/api/tasks` | Create a new task |
| PUT | `/api/tasks/<id>` | Update a task |
| DELETE | `/api/tasks/<id>` | Delete a task |

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/flask-todo.git
cd flask-todo
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

3. Install dependencies:
```bash
pip install flask flask-sqlalchemy pytest pytest-cov flasgger
```

4. Run the application:
```bash
python app.py
```

5. Open your browser:
   - Web app: http://localhost:5000/
   - API docs (Swagger): http://localhost:5000/apidocs/

## Running Tests

```bash
pytest test_api.py -v
```

### With Coverage Report

```bash
pytest test_api.py --cov=app --cov-report=term-missing -v
```

## API Usage Examples

### Create a Task
```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "complete": false}'
```

### Get All Tasks
```bash
curl http://localhost:5000/api/tasks
```

### Update a Task
```bash
curl -X PUT http://localhost:5000/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"complete": true}'
```

### Delete a Task
```bash
curl -X DELETE http://localhost:5000/api/tasks/1
```

## Branch Information

- `master` — Original project by Patrick Loeber
- `feature/tasks-api` — My REST API additions