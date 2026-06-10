from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)

# /// = relative path, //// = absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

VALID_PRIORITIES = ["low", "medium", "high"]


class Todo(db.Model):
    """Model representing a Todo item."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(500), nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.String(10), nullable=True)

    def to_dict(self):
        """Serialize the Todo object to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "complete": self.complete,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "priority": self.priority
        }


# Existing HTML routes (unchanged behavior)

@app.route("/")
def home():
    todo_list = Todo.query.all()
    return render_template("base.html", todo_list=todo_list)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    description = request.form.get("description") or None
    due_date_str = request.form.get("due_date") or None
    priority = request.form.get("priority") or None

    due_date = None
    if due_date_str:
        try:
            due_date = date.fromisoformat(due_date_str)
        except ValueError:
            due_date = None

    new_todo = Todo(
        title=title,
        complete=False,
        description=description,
        due_date=due_date,
        priority=priority
    )
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


# REST API routes

@app.route("/api/todos", methods=["GET"])
def api_get_todos():
    """Return a list of all todo items."""
    todos = Todo.query.all()
    return jsonify([todo.to_dict() for todo in todos]), 200


@app.route("/api/todos/<int:todo_id>", methods=["GET"])
def api_get_todo(todo_id):
    """Return a single todo item by ID. Returns 404 if not found."""
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        return jsonify({"error": "Todo not found"}), 404
    return jsonify(todo.to_dict()), 200


@app.route("/api/todos", methods=["POST"])
def api_create_todo():
    """
    Create a new todo item.
    Expects JSON body: {
        "title": "some text",          (required)
        "description": "some text",    (optional)
        "due_date": "YYYY-MM-DD",      (optional)
        "priority": "low|medium|high"  (optional)
    }
    Returns 400 if title is missing, empty, or other fields are invalid.
    """
    data = request.get_json()
    if not data or not data.get("title", "").strip():
        return jsonify({"error": "Title is required"}), 400

    # Validate due_date if provided
    due_date = None
    if "due_date" in data and data["due_date"] is not None:
        try:
            due_date = date.fromisoformat(data["due_date"])
        except ValueError:
            return jsonify({"error": "due_date must be in YYYY-MM-DD format"}), 400

    # Validate priority if provided
    priority = None
    if "priority" in data and data["priority"] is not None:
        if data["priority"] not in VALID_PRIORITIES:
            return jsonify({"error": f"priority must be one of: {', '.join(VALID_PRIORITIES)}"}), 400
        priority = data["priority"]

    description = data.get("description") or None

    new_todo = Todo(
        title=data["title"].strip(),
        complete=False,
        description=description,
        due_date=due_date,
        priority=priority
    )
    db.session.add(new_todo)
    db.session.commit()
    return jsonify(new_todo.to_dict()), 201


@app.route("/api/todos/<int:todo_id>", methods=["PUT"])
def api_update_todo(todo_id):
    """
    Update an existing todo item by ID.
    Accepts any combination of:
    {
        "title": "new text",
        "complete": true,
        "description": "new text",
        "due_date": "YYYY-MM-DD",
        "priority": "low|medium|high"
    }
    Returns 404 if not found, 400 if fields are invalid.
    """
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        return jsonify({"error": "Todo not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400 # pragma: no cover

    if "title" in data:
        if not isinstance(data["title"], str) or not data["title"].strip():
            return jsonify({"error": "Title cannot be empty"}), 400
        todo.title = data["title"].strip()

    if "complete" in data:
        if not isinstance(data["complete"], bool):
            return jsonify({"error": "'complete' must be a boolean"}), 400
        todo.complete = data["complete"]

    if "description" in data:
        todo.description = data["description"] or None

    if "due_date" in data:
        if data["due_date"] is None:
            todo.due_date = None
        else:
            try:
                todo.due_date = date.fromisoformat(data["due_date"])
            except ValueError:
                return jsonify({"error": "due_date must be in YYYY-MM-DD format"}), 400

    if "priority" in data:
        if data["priority"] is None:
            todo.priority = None
        elif data["priority"] not in VALID_PRIORITIES:
            return jsonify({"error": f"priority must be one of: {', '.join(VALID_PRIORITIES)}"}), 400
        else:
            todo.priority = data["priority"]

    db.session.commit()
    return jsonify(todo.to_dict()), 200


@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def api_delete_todo(todo_id):
    """Delete a todo item by ID. Returns 404 if not found."""
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        return jsonify({"error": "Todo not found"}), 404

    db.session.delete(todo)
    db.session.commit()
    return jsonify({"message": "Todo deleted successfully"}), 200


if __name__ == "__main__":  # pragma: no cover
    with app.app_context():
        db.create_all()
    app.run(debug=True)