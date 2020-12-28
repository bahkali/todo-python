from flask import Flask,request , abort,  render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy 
import sys
# from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Jerico05@localhost:5433/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description= db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    def __repr(self):
        return f'<Todo {self.id} {self.description}'
#description-value = request.form.get('description')

#data_str = request.data
#data_dict = json.loads(data_str)

# db.create_all() replace by flask db migrate

@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body={}
    try:
        # description = request.form.get('description', '')
        description = request.get_json()['description']
        todo = Todo(description=description)
        db.session.add(todo)
        db.session.commit()
        # return redirect(url_for('index'))
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


@app.route('/')
def index():
    return render_template('index.html', data=Todo.query.all())


if __name__ == "__main__":
    app.run()
