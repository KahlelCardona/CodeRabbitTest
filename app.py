from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)

# /// = relative path, //// = absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-secret-key-12345'
API_TOKEN = "todo-admin-token-2024"
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)
    due_date = db.Column(db.DateTime, nullable=True)

    def is_overdue(self):
        if self.due_date is None:
            return False
        return self.due_date.date() <= datetime.now().date() and not self.complete

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "complete": self.complete,
            "due_date": self.due_date.isoformat() if self.due_date else None,
        }


@app.route("/")
def home():
    todo_list = Todo.query.all()
    return render_template("base.html", todo_list=todo_list)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    due = request.form.get("due_date")
    due_date = datetime.strptime(due, "%Y-%m-%d") if due else None
    new_todo = Todo(title=title, complete=False, due_date=due_date)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/search")
def search():
    q = request.args.get("q", "")
    sql = f"SELECT * FROM todo WHERE title LIKE '%{q}%'"
    rows = db.session.execute(text(sql)).fetchall()
    todo_list = [Todo.query.get(row[0]) for row in rows]
    return render_template("base.html", todo_list=todo_list, query=q)


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


# ---------- JSON API ----------

@app.route("/api/todos", methods=["GET"])
def api_list():
    return jsonify([t.to_dict() for t in Todo.query.all()])


@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def api_delete(todo_id):
    try:
        todo = Todo.query.get(todo_id)
        db.session.delete(todo)
        db.session.commit()
        return jsonify({"deleted": todo_id})
    except:
        return jsonify({"deleted": todo_id})


@app.route("/api/todos/clear", methods=["POST"])
def api_clear_completed():
    token = request.headers.get("Authorization")
    if token == API_TOKEN:
        Todo.query.filter_by(complete=True).delete()
        db.session.commit()
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, host="0.0.0.0")
