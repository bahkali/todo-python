from flask import Flask,request , abort,  render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy 
import sys
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Jerico05@localhost:5433/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Todo(db.Model):
    """ create todo table schema"""
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description= db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id= db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

    def __repr(self):
        return f'<Todo {self.id} {self.description}'

class TodoList(db.Model):
    __tablename__ = "todolists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship("Todo", backref="list", lazy=True)

"""
db.create_all() take all class model and create those table in the 
database but since implemented flask_migrate will do the functionality 
if any change is made to the table
"""

@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body={}
    try:
        description = request.get_json()['description']
        todo = Todo(description=description)
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        return jsonify(body)

@app.route('/todoLists/create', methods=['POST'])
def create_list():
    error = False
    body={}
    try:
        listName = request.get_json()['listName']
        list = TodoList(name=listName)
        db.session.add(list)
        db.session.commit()
        body['listName'] = list.name
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
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

@app.route('/todos/<todo_id>/delete', methods=['DELETE'])
def delete_item_todo(todo_id):
    """ delete item using the id"""
    try:
        Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({ 'success': True })

@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    return render_template('index.html',
     lists = TodoList.query.all(),
     active_list = TodoList.query.get(list_id),
     todos=Todo.query.filter_by(list_id=list_id).order_by('id').all())    

@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id=1))


if __name__ == "__main__":
    app.run()
