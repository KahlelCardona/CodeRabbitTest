from flask import Blueprint, jsonify, request

api = Blueprint("api", __name__)

def get_db_and_todo():
    from app import db, Todo, app
    return db, Todo, app

@api.route("/api/todos", methods=["GET"])
def get_todos():
    db, Todo, app = get_db_and_todo()
    with app.app_context():
        todos = Todo.query.all()
        return jsonify([
            {"id": todo.id, "title": todo.title, "complete": todo.complete}
            for todo in todos
        ]), 200

@api.route("/api/todos/<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
    db, Todo, app = get_db_and_todo()
    with app.app_context():
        todo = Todo.query.get(todo_id)
        if todo is None:
            return jsonify({"error": "Todo not found"}), 404
        return jsonify({
            "id": todo.id,
            "title": todo.title,
            "complete": todo.complete
        }), 200

@api.route("/api/todos", methods=["POST"])
def create_todo():
    db, Todo, app = get_db_and_todo()
    data = request.get_json()
    if not data or "title" not in data or not data["title"].strip():
        return jsonify({"error": "A 'title' field is required"}), 400
    with app.app_context():
        new_todo = Todo(title=data["title"].strip(), complete=False)
        db.session.add(new_todo)
        db.session.commit()
        return jsonify({
            "id": new_todo.id,
            "title": new_todo.title,
            "complete": new_todo.complete
        }), 201

@api.route("/api/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    db, Todo, app = get_db_and_todo()
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    with app.app_context():
        todo = Todo.query.get(todo_id)
        if todo is None:
            return jsonify({"error": "Todo not found"}), 404
        if "title" in data:
            if not data["title"].strip():
                return jsonify({"error": "Title cannot be empty"}), 400
            todo.title = data["title"].strip()
        if "complete" in data:
            if not isinstance(data["complete"], bool):
                return jsonify({"error": "'complete' must be true or false"}), 400
            todo.complete = data["complete"]
        db.session.commit()
        return jsonify({
            "id": todo.id,
            "title": todo.title,
            "complete": todo.complete
        }), 200

@api.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    db, Todo, app = get_db_and_todo()
    with app.app_context():
        todo = Todo.query.get(todo_id)
        if todo is None:
            return jsonify({"error": "Todo not found"}), 404
        db.session.delete(todo)
        db.session.commit()
        return jsonify({"message": f"Todo {todo_id} deleted successfully"}), 200