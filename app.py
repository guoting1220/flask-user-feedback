"""Feedback Flask app."""
from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import Unauthorized
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
from werkzeug.exceptions import Unauthorized

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgres:///flask-feedback"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "secret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)


@app.route("/")
def homepage():
    """home page"""

    return redirect("/register")

@app.route("/register", methods=['GET', 'POST'])
def refister():
    """show register form"""

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data

        if User.query.get(username):
            flash("The username has been taken! Please try a different one!")
            return redirect("/register")
            
        password = form.password.data        
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data

        user = User.register(username, password, first_name, last_name, email)

        db.session.add(user)
        db.session.commit()
        session["username"] = user.username

        return redirect(f"/users/{user.username}")

    else:
        return render_template("user/register.html", form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    """show login form"""
    
    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = LoginForm()
   
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:        
            session["username"] = user.username
            flash("Welcome back!", "success")
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ["Invalid username/password."]

    return render_template("user/login.html", form=form)


@app.route("/logout")
def logout():
    """user logout"""

    session.pop("username")

    return redirect("/login")
    

@app.route("/users/<username>")
def show_user_info(username):
    """show the info of the login user"""

    if "username" not in session or session["username"] != username:
        # raise Unauthorized()
        flash("Please login with correct account!") 
        return redirect("/login")

    user = User.query.get_or_404(username)
    feedbacks = Feedback.query.filter_by(username=username)

    return render_template("user/show.html", user=user, feedbacks=feedbacks)


@app.route("/users/<username>/delete", methods=['POST'])
def delete_user(username):
    """delete the user including all his feedbacks"""

    if "username" not in session or session["username"] != username:
        raise Unauthorized()

    user = User.query.get_or_404(username)
    db.session.delete(user)
    db.session.commit()
    session.pop("username")
    flash("User deleted!")

    return redirect("/")



@app.route("/users/<username>/feedback/add", methods=['GET', 'POST'])
def add_feedback(username):
    """show add feedback form and handle the adding"""

    if "username" not in session or session["username"] != username:
        flash("Please login with correct account!")
        return redirect("/login")

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(title=title, content=content, username=username)

        db.session.add(feedback)
        db.session.commit()
        flash("Feedback added!")
        return redirect(f"/users/{username}")

    else:
        return render_template("feedback/new.html", form=form)    


@app.route("/feedback/<feedback_id>/update", methods=['GET', 'POST'])
def edit(feedback_id):
    """edit the feedback"""

    feedback = Feedback.query.get_or_404(feedback_id)
  
    if "username" not in session or session["username"] != feedback.username:
        raise Unauthorized()

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        flash("Feedback updated!")
        return redirect(f"/users/{feedback.username}")
    
    return render_template("feedback/edit.html", form=form, feedback=feedback)


@app.route("/feedback/<feedback_id>/delete", methods=['GET', 'POST'])
def delete_feedback(feedback_id):
    """delete the feedback"""

    feedback = Feedback.query.get_or_404(feedback_id)

    if "username" not in session or session["username"] != feedback.username:
        raise Unauthorized()

    db.session.delete(feedback)
    db.session.commit()  
    flash("Feedback deleted!")
    return redirect(f"/users/{feedback.username}")

