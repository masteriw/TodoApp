import sys
from flask import Flask, jsonify, redirect, render_template, request, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/todoapp'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Todo(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  description = db.Column(db.String(), nullable = False)
  completed = db.Column(db.Boolean(), nullable = False, default = False)
  list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

  def __repr__(self):
      return f'<Todo> id = {self.id} description = {self.description} completed = {self.completed}>'
  
class TodoList(db.Model):
  __tablename__ = 'todolists'
  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(), nullable = False)
  todos = db.relationship('Todo', backref='list', lazy=True)

  def __repr__(self):
    return f'<TodoList> id = {self.id} name = {self.name} todos = {self.todos}>'

@app.route('/')
def index():
  list_id = TodoList.query.first().id
  return redirect(url_for('get_list_todos', list_id = list_id))

@app.route('/lists/<list_id>')
def get_list_todos(list_id):
  return render_template('index.html',
  lists=TodoList.query.all(),
  active_list=TodoList.query.get(list_id),
  todos=Todo.query.filter_by(list_id=list_id).order_by('id').all()
)

@app.route('/todos/create', methods=['POST'])
def create():
  error = False
  body = {}
  try:
    print('cheguei')
    description = request.get_json()['description']
    list_id = request.get_json()['list_id']
    todo = Todo(description=description, list_id = list_id)
    active_list = TodoList.query.get(list_id)
    todo.list = active_list
    db.session.add(todo)
    db.session.commit()
    body['description'] = todo.description
    body['id'] = todo.id
    body['completed'] = todo.completed
    body['list_id'] = todo.list_id
  except:
    db.session.rollback()
    error=True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
    return jsonify(body)
    
@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
  try:
    completed = request.get_json()['completed']
    todo = Todo.query.get(todo_id)
    todo.completed = completed
    db.session.commit() 
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))

@app.route('/todos/delete', methods=['POST'])
def delete():
  try:
    todo_id = request.get_json()['todoId']
    Todo.query.filter_by(id=todo_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
    print('Erro:')
    print (sys.exc_info())
  finally:
    db.session.close()
  return jsonify(todo_id)