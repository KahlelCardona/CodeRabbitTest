from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# /// = relative path, //// = absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Todo(db.Model):
    """Model representing a Todo item."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)

    def to_dict(self):
        """Serialize the Todo object to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "complete": self.complete
        }


# ─────────────────────────────────────────
# Existing HTML routes (unchanged)
# ─────────────────────────────────────────

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


# ─────────────────────────────────────────
# REST API routes
# ─────────────────────────────────────────

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
    Expects JSON body: { "title": "some text" }
    Returns 400 if title is missing or empty.
    """
    data = request.get_json()
    if not data or not data.get("title", "").strip():
        return jsonify({"error": "Title is required"}), 400

    new_todo = Todo(title=data["title"].strip(), complete=False)
    db.session.add(new_todo)
    db.session.commit()
    return jsonify(new_todo.to_dict()), 201


@app.route("/api/todos/<int:todo_id>", methods=["PUT"])
def api_update_todo(todo_id):
    """
    Update an existing todo item by ID.
    Accepts optional JSON fields: { "title": "new text", "complete": true }
    Returns 404 if not found, 400 if no valid fields provided.
    """
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        return jsonify({"error": "Todo not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400 # pragma: no cover

    if "title" in data:
        if not data["title"].strip():
            return jsonify({"error": "Title cannot be empty"}), 400
        todo.title = data["title"].strip()

    if "complete" in data:
        if not isinstance(data["complete"], bool):
            return jsonify({"error": "'complete' must be a boolean"}), 400
        todo.complete = data["complete"]

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