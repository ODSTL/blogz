# Can we hurry this along please? I have a plane to catch.
# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName

from flask import Flask, request, redirect, render_template, session
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
        self.user = owner

@app.before_request
def require_login():
    allowed_routes = ['index', 'all_blogs', 'singleUser', 'signup', 'login']
    if request.endpoint  not in allowed_routes and "username" not in session:
        return redirect('/login')

@app.route("/", methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route("/newpost", methods= ['POST', 'GET'])
def AddPost():
    error = {"title_blank": "", "body_blank": ""}
    new_body = ""
    new_title = ""

    if request.method == 'POST':
        title = request.form["title"]
        body = request.form["body"]
        owner = User.query.filter_by(username=session['username']).first()
        if title == "":
            error["t_blank"] = "Please enter a title."
        if body == "":
            error["b_blank"] = "Please write a post."

        if error["t_blank"] == "" and error["b_blank"] == "":
            new_blog = Blog(title, body, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect("/all_blogs?id="+str(new_blog.id))

        return render_template('newpost.html', title= "Please add a post.",
            body= body, owner= owner, t_blank= error["t_blank"],
             b_blank= error["b_blank"])

    else:
        return render_template('newpost.html')

@app.route("/all_blogs", methods=['GET'])
def AllBlogs():
    if request.args:
        id = request.args.get ('id')
        post = Blog.query.get(id)
        return render_template('singlepost.html', entry=post)
    else:
        post = blog.query.all()
        return render_template("all_blogs.html", blog=post)

@app.route("/singleUser", methods=['POST', 'GET'])
def SingleUser():

    user = request.args.get('user')
    blogs = Blog.query.filter_by(owner_id= user).all()

    return render_template("singleUser.html", blogs= blogs)

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    error = {"u_error": "", "p_error": "", "v_error": ""}
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        username_value = ""
        password_value = ""
        verify_value = ""
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            username_value = "Please choose a different username."
        elif username == "":
            username_value = "Username cannot be blank."
        elif " " in username:
            username_value = "Username cannot contain spaces."

        if password == "":
           password_value = "Password cannot be blank."
        elif len(password) < 5:
           password_value = "Password must contain more than 5 characters."
        elif " " in password:
           password_value = "Password cannot contain spaces."

        if verify == "":
           verify_value = "Please complete all fields."
        elif verify != password:
           verify_value = "Request could not be verified. Please try again."
        else:
           if password != verify:
               error["v_error"] = "Passwords must match."

        if not existing_user and not username_value and not password_value and not verify_value:
           user = User(username, password)
           db.session.add(user)
           db.session.commit()
           session['username'] = username
           return redirect('/newpost')

        else:
           return render_template("signup.html",
            username_value=username_value, password_value=password_value,
            verify_value=verify_value, username=username)

    return render_template("signup.html")


@app.route("/login", methods=['POST', 'GET'])
def login():
    error = {"u_error": "", "p_error": ""}
    username = ""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        u_error = ''
        p_error = ''
        existing_user = User.query.filter_by(username=username).first()

        if not username:
            u_error = "Invalid Username."
        if not password:
            p_error = "Invalid Password."
        if user and user.password == password:
            session['username'] = username
            return redirect('/all_blogs')
        else:
            p_error = "Invalid Password."

        return render_template("login.html", u_error= u_error,
            p_error= p_error)
    return render_template("login.html")


@app.route("/logout")
def logout():
    del session['username']
    return redirect('/')

if __name__ == '__main__':
    app.run()
