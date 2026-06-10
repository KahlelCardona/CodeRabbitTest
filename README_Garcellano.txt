Required Installs:
Python
Git

Dependencies:
pip install Flask
pip install Flask-SQLAlchemy
pip install pytest
pip install pytest-cov

Step by step to run the app:
1. Clone the repository
git clone https://github.com/DCG06/flask-todo.git
cd flask-todo
2. Switch to my branch 
git checkout feature/todo-rest-api
3. Create Virtual Env
python -m venv venv
venv\Scripts\activate
4.Install Dependencies Above
5. initialize database

python

from app import app, db
with app.app_context():
    db.create_all()
exit()

6. Run the app

flask run

7. Run Tests
pytest test_api.py -v
pytest --cov=app --cov-report=term-missing test_api.py

CHANGES
- REST API with full CRUD endpoints for Todo items
- New inputs: description, due date, and priority
- Error handling with HTTP status codes (200, 201, 400, 404)
- Unit tests with 100% coverage using pytest
- Both positive and negative test cases for all endpoints
