from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# /// = relative path, //// = absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)
    priority = db.Column(db.Integer, default=3)
    due_date = db.Column(db.Date, nullable=True)


@app.route("/")
def home():
    sort_by = request.args.get('sort_by', 'id')
    order = request.args.get('order', 'asc')
    
    if sort_by == 'priority':
        if order == 'asc':
            todo_list = Todo.query.order_by(Todo.priority.asc()).all()
        else:
            todo_list = Todo.query.order_by(Todo.priority.desc()).all()
    elif sort_by == 'due_date':
        if order == 'asc':
            todo_list = Todo.query.order_by(Todo.due_date.asc().nulls_last()).all()
        else:
            todo_list = Todo.query.order_by(Todo.due_date.desc().nulls_last()).all()
    else:
        if order == 'asc':
            todo_list = Todo.query.order_by(Todo.id.asc()).all()
        else:
            todo_list = Todo.query.order_by(Todo.id.desc()).all()
    
    return render_template("base.html", todo_list=todo_list, sort_by=sort_by, order=order)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    priority = request.form.get("priority", 3, type=int)
    due_date_str = request.form.get("due_date")
    
    due_date = None
    if due_date_str:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
    
    new_todo = Todo(title=title, complete=False, priority=priority, due_date=due_date)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/update/<int:todo_id>")
def update(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/edit", methods=["POST"])
def edit():
    todo_id = request.form.get("id", type=int)
    title = request.form.get("title")
    priority = request.form.get("priority", 3, type=int)
    due_date_str = request.form.get("due_date")
    
    todo = Todo.query.filter_by(id=todo_id).first()
    if todo:
        todo.title = title
        todo.priority = priority
        if due_date_str:
            todo.due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        else:
            todo.due_date = None
        db.session.commit()
    return redirect(url_for("home"))


@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home"))

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
