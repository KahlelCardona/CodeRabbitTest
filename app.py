from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__) # 创建Web应用，app 就是这个Web应用本身，__name__ 表示当前 Python 模块的名字。

# /// = relative path, //// = absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite' # 数据库配置
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) # 创建数据库对象


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)


@app.route("/") # 它告诉 Flask：当浏览器访问 / 时，应该执行下面这个函数。
def home():
    todo_list = Todo.query.all() # 从 Todo 数据库表中，把所有任务查询出来。
    return render_template("base.html", todo_list=todo_list) # 使用 base.html 模板，并把 todo_list 传给它。


@app.route("/add", methods=["POST"]) # GET 通常用于获取数据，而 POST 通常用于提交数据/创建数据。
def add():
    title = request.form.get("title")
    new_todo = Todo(title=title, complete=False)
    db.session.add(new_todo)
    db.session.commit() # 真正把之前的数据库操作提交到 SQLite。
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

if __name__ == "__main__": # 如果这个文件是直接运行的，就执行下面的代码。
    with app.app_context():
        db.create_all()
    app.run(debug=True)
