# Can we hurry this along please? I have a plane to catch.
# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName

from flask import Flask, request, redirect, render_template, session
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
        
        return render_template('singlepost.html', post=entry)

    else:
        entry = Blog.query.all()
        return render_template('blog.html', blog=entry)

#@app.route('/newpost', )

@app.route('/newpost', methods=['GET', 'POST'])
def new_post():

    if request.method == 'POST':

        title = request.form['title']
        body = request.form['body']
        fish = Blog(title, body)
        t_error=''
        b_error=''
        if not title:
            t_error = "Please Enter A Post Title"
        if not body:
            b_error = "Please Enter A Post Body"
        if not t_error and not b_error:
            post = Blog(title, body)
            db.session.add(post)
            db.session.commit()
            return redirect('/blog?id=' + str(post.id))

        return render_template('newpost.html', t_error=t_error, b_error=b_error, title=title, body=body)
    else:
        return render_template('newpost.html')

if __name__ == '__main__':
    app.run()
