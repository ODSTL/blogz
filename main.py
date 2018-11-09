# Can we hurry this along please? I have a plane to catch.
# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName

from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:bloggerguy@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'secret123key456'

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username  = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

@app.before_request
def require_login():
    allowed_routes = ['/', 'newpost', 'signup', 'login']
    if request.endpoint  not in allowed_routes and "username" not in session:
        return redirect('/login')

@app.route("/", methods=['POST', 'GET'])
def index():
    users = User.query.order_by(User.id.asc()).all()
    return render_template('index.html', users=users)

@app.route("/newpost", methods= ['POST', 'GET'])
def AddPost():
    new_body = ""
    new_title = ""

    if request.method == 'POST':
        title = request.form["title"]
        body = request.form["body"]
        owner = User.query.filter_by(username=session['username']).first()
        new_post = Blog(title, body, owner)

        if new_post.title == "":
            flash("Please enter a title.", "error")
        if new_post.body == "":
            flash("Please write a post.", "error")

        if new_post.title != "" and new_post.body != "":
            db.session.add(new_post)
            db.session.commit()
            return redirect("/all_blogs?id="+str(new_post.id))

        else:
            return render_template('newpost.html')
    return render_template('newpost.html')

@app.route("/all_blogs", methods=['GET'])
def AllBlogs():
    if "user" in request.args:
        user_id = request.args.get ('user')
        post = Blog.query.filter_by(id=id).first()
        return render_template('singlepost.html', title="Your Posts", post=post)

    posts = Blog.query.order_by(Blog.id.asc())
    return render_template('all_blogs.html', title="List", posts=posts)

@app.route("/singleUser", methods=['POST', 'GET'])
def SingleUser():

    user = request.args.get('user')
    blogs = Blog.query.filter_by(owner_id=user).all()

    return render_template('singleUser.html', blogs= blogs)

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()

        if existing_user and existing_user.password == password:
            session['username'] = username
            flash("You are logged in.")
            return redirect('/all_blogs')
        if existing_user and existing_user.password != password:
            flash("Password Incorrect.", "error")

    return render_template("login.html")


@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        if username == "":
            flash("Username cannot be blank.", "error")
        if len(username) < 3:
            flash("Username must contain more than 3 characters.", "error")
        if " " in username:
            flash("Username cannot contain spaces.", "error")

        if password == "":
            flash("Password cannot be blank.", "error")
        if len(password) < 3:
            flash("Password must contain more than 3 characters.", "error")
        if " " in password:
            flash("Password cannot contain spaces.", "error")

        if verify == "":
            flash("Please complete all fields.", "error")
        if verify != password:
            flash("Request could not be verified. Please try again.", "error")

            if not existing_user and not username and not password and not verify:
                user = User(username, password)
                db.session.add(user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                return render_template('signup.html')

    return render_template("signup.html")





@app.route("/logout")
def logout():
    del session['username']
    return redirect('/')

if __name__ == '__main__':
    app.run()
