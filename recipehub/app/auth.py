from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app import mongo, bcrypt

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = mongo.db.users.find_one({'email': email})

        if user and check_password_hash(user['password'], password):
            user_obj = User(user)
            login_user(user_obj)
            return redirect(url_for('main.profile'))
        else:
            flash('Login failed. Check your email and password.')

    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        password_hash = generate_password_hash(password)

        user = {
            'email': email,
            'username': username,
            'password': password_hash
        }

        mongo.db.users.insert_one(user)
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
