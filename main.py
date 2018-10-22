# Can we hurry this along please? I have a plane to catch.
# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName

from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:bloggernuts@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog', methods=['GET'])
def blog():

    if request.args:
        id = request.args.get('id')
        entry = Blog.query.get(id)
        return render_template('singlepost.html', new_post=entry)

    else:
        entry = Blog.query.all()
        return render_template('blog.html', blog=entry)


@app.route('/delete-task', methods=['POST'])
def delete_task():

    task_id = int(request.form['task-id'])
    task = Blog.query.get(task_id)
    task.completed = True
    db.session.add(task)
    db.session.commit()

    return redirect('/')


if __name__ == '__main__':
    app.run()
