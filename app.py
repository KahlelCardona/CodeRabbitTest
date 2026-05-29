# ─────────────────────────────────────────────
# IMPORTS — bringing in the tools we need
# ─────────────────────────────────────────────

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger, swag_from

# ─────────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────────

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Swagger configuration — sets up the docs page
app.config['SWAGGER'] = {
    'title': 'Flask Todo API',
    'uiversion': 3,
    'description': 'A REST API for managing todo tasks',
    'version': '1.0.0'
}

db = SQLAlchemy(app)
swagger = Swagger(app)

# ─────────────────────────────────────────────
# DATABASE MODEL (the "Todo" table blueprint)
# ─────────────────────────────────────────────

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.Boolean, default=False)

    def to_dict(self):
        """Convert a Todo object to a Python dictionary (for JSON responses)"""
        return {
            'id': self.id,
            'title': self.title,
            'complete': self.complete
        }

# ─────────────────────────────────────────────
# ORIGINAL WEB ROUTES (keep these — don't delete)
# ─────────────────────────────────────────────

@app.route("/")
def home():
    todo_list = Todo.query.all()
    return render_template("base.html", todo_list=todo_list)

@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    new_todo = Todo(title=title, complete=False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/update/<int:todo_id>")
def update(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home"))

# ─────────────────────────────────────────────
# REST API ROUTES (your new feature!)
# ─────────────────────────────────────────────

# ── READ ALL ──────────────────────────────────
@app.route("/api/tasks", methods=["GET"])
def get_all_tasks():
    """
    Get all tasks
    ---
    tags:
      - Tasks
    responses:
      200:
        description: A list of all tasks
        schema:
          type: array
          items:
            properties:
              id:
                type: integer
                example: 1
              title:
                type: string
                example: Buy groceries
              complete:
                type: boolean
                example: false
    """
    tasks = Todo.query.all()
    return jsonify([task.to_dict() for task in tasks]), 200


# ── READ ONE ──────────────────────────────────
@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    """
    Get a single task by ID
    ---
    tags:
      - Tasks
    parameters:
      - name: task_id
        in: path
        type: integer
        required: true
        description: The ID of the task
    responses:
      200:
        description: The task was found
        schema:
          properties:
            id:
              type: integer
              example: 1
            title:
              type: string
              example: Buy groceries
            complete:
              type: boolean
              example: false
      404:
        description: Task not found
        schema:
          properties:
            error:
              type: string
              example: Task not found
    """
    task = Todo.query.get(task_id)
    if task is None:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify(task.to_dict()), 200


# ── CREATE ────────────────────────────────────
@app.route("/api/tasks", methods=["POST"])
def create_task():
    """
    Create a new task
    ---
    tags:
      - Tasks
    parameters:
      - in: body
        name: body
        required: true
        schema:
          required:
            - title
          properties:
            title:
              type: string
              example: Buy groceries
            complete:
              type: boolean
              example: false
    responses:
      201:
        description: Task created successfully
        schema:
          properties:
            id:
              type: integer
              example: 1
            title:
              type: string
              example: Buy groceries
            complete:
              type: boolean
              example: false
      400:
        description: Missing required field
        schema:
          properties:
            error:
              type: string
              example: Title is required
    """
    data = request.get_json()

    # Validate: data must exist and title must be present and not empty
    if not data or 'title' not in data or not data['title'].strip():
        return jsonify({'error': 'Title is required'}), 400

    new_task = Todo(
        title=data['title'].strip(),
        complete=data.get('complete', False)  # defaults to False if not provided
    )
    db.session.add(new_task)
    db.session.commit()

    return jsonify(new_task.to_dict()), 201


# ── UPDATE ────────────────────────────────────
@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    """
    Update an existing task
    ---
    tags:
      - Tasks
    parameters:
      - name: task_id
        in: path
        type: integer
        required: true
        description: The ID of the task to update
      - in: body
        name: body
        required: true
        schema:
          properties:
            title:
              type: string
              example: Updated task title
            complete:
              type: boolean
              example: true
    responses:
      200:
        description: Task updated successfully
        schema:
          properties:
            id:
              type: integer
              example: 1
            title:
              type: string
              example: Updated task title
            complete:
              type: boolean
              example: true
      400:
        description: No valid fields provided
        schema:
          properties:
            error:
              type: string
              example: No valid fields provided
      404:
        description: Task not found
        schema:
          properties:
            error:
              type: string
              example: Task not found
    """
    task = Todo.query.get(task_id)
    if task is None:
        return jsonify({'error': 'Task not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No valid fields provided'}), 400

    # Only update the fields that were actually sent
    if 'title' in data:
        if not data['title'].strip():
            return jsonify({'error': 'Title cannot be empty'}), 400
        task.title = data['title'].strip()

    if 'complete' in data:
        task.complete = data['complete']

    db.session.commit()
    return jsonify(task.to_dict()), 200


# ── DELETE ────────────────────────────────────
@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """
    Delete a task
    ---
    tags:
      - Tasks
    parameters:
      - name: task_id
        in: path
        type: integer
        required: true
        description: The ID of the task to delete
    responses:
      200:
        description: Task deleted successfully
        schema:
          properties:
            message:
              type: string
              example: Task deleted successfully
      404:
        description: Task not found
        schema:
          properties:
            error:
              type: string
              example: Task not found
    """
    task = Todo.query.get(task_id)
    if task is None:
        return jsonify({'error': 'Task not found'}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully'}), 200


# ─────────────────────────────────────────────
# RUN THE APP
# ─────────────────────────────────────────────

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)