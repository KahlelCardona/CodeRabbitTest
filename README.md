# Flask Todo App — with REST API

This is a fork of [patrickloeber/flask-todo](https://github.com/patrickloeber/flask-todo), a simple Todo web application built with Flask and SQLAlchemy.

## What is the original app?

The original app is a simple Todo list web application. You open it in your browser, type a task, and click Add. You can also mark tasks as complete or delete them. But all of that only works through the browser — there is no way for another program to talk to it.

## What did I add?

I added a REST API. This means other programs (like Postman, a mobile app, or another website) can now interact with the todos by sending HTTP requests and receiving JSON responses — without touching the browser at all.

This is useful because:
- A mobile app could use the API to sync todos
- Another service could automatically create or delete todos
- Developers can test the app without opening a browser

## How does it work?

The API has 5 routes that cover full CRUD operations:

- GET /api/todos — returns a list of all todos as JSON
- GET /api/todos/id — returns one specific todo by its ID
- POST /api/todos — creates a new todo (send a title in the request body)
- PUT /api/todos/id — updates an existing todo (change title or complete status)
- DELETE /api/todos/id — deletes a todo permanently

All responses are in JSON format. The API also handles errors properly:
- 200 means the request was successful
- 201 means a new todo was successfully created
- 400 means the request was missing something or had bad data
- 404 means the todo ID does not exist

## Files I Added

### api.py
Contains all 5 API routes with full CRUD functionality and error handling.
Uses Flask Blueprint to keep the API separate from the main app code.

### test_api.py
Contains 18 unit tests written with pytest.
Tests cover all CRUD operations with both positive and negative test cases.
Positive tests check that things work correctly.
Negative tests check that errors are handled properly (missing data, wrong ID, etc.)

## How to Run

1. Clone and switch to the feature branch:
   git clone https://github.com/CarloGarcellano/flask-todo.git
   cd flask-todo
   git checkout feature/rest-api

2. Install dependencies:
   pip install flask flask-sqlalchemy pytest pytest-cov

3. Run the app:
   python app.py

4. Visit the app in your browser:
   http://127.0.0.1:5000

5. Test the API:
   http://127.0.0.1:5000/api/todos

6. Run the unit tests:
   pytest test_api.py -v

## Original Repository
https://github.com/patrickloeber/flask-todo