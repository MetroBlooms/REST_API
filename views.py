#http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
#https://github.com/mrjoes/flask-admin/blob/master/examples/auth/app.py

from flask import render_template, flash, redirect, session, jsonify, request
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from flask.ext import login
from app import app, db, models
from forms import LoginForm
from wtforms import validators

User = models.User


# intialize Flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(id):
        return db.session.query(User).get(int(id))

# Initialize flask-login
init_login()


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    session['username'] = None

    # get instance of User class
    def get_user():
        return User.query.filter_by(username=form.username.data).first()

    if form.validate_on_submit():

        form_data = form.username.data

        # validate the user...
        user = get_user()

        session['username'] = user.username

        if form_data is None or form_data == "":
            flash('Invalid login. Please try again.')
            return render_template("login.html", title='Sign In', form=form)
        if user is None:
            username = form.username.data
            # add logic to create new user
        else:
            if User.verify_password(user, form.password.data):
                login_user(user)
                flash("Logged in successfully.")
                return redirect('/api/TestMe')
            else:
                return 'Invalid password!'

    return render_template("login.html", title='Sign In', form=form)