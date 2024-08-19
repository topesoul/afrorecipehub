from flask import render_template, redirect, url_for, request, flash, session
from recipehub import app, mongo, bcrypt
from recipehub.forms import RegistrationForm, LoginForm
from flask_login import login_user, current_user, logout_user, login_required
from bson.objectid import ObjectId
from recipehub.models import User

@app.route('/')
def index():
    return redirect(url_for('recipes.get_recipes'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = {
            "username": form.username.data,
            "email": form.email.data,
            "password": hashed_password,
            "points": 0,  # Initialize points for the new user
            "bookmarked_recipes": [],  # Initialize an empty list for bookmarked recipes
            "isAdmin": False  # Default to non-admin user
        }
        mongo.db.users.insert_one(user)
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"email": form.email.data})
        if user and bcrypt.check_password_hash(user["password"], form.password.data):
            user_obj = User.get_user_by_id(user["_id"])
            login_user(user_obj)
            # Store admin status in session
            session['is_admin'] = user.get('isAdmin', False)
            return redirect(url_for('recipes.get_recipes'))
        else:
            flash('Login unsuccessful. Please check your email and password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('is_admin', None)
    return redirect(url_for('recipes.get_recipes'))