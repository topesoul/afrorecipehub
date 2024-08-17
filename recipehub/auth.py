from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from recipehub.forms import RegistrationForm, LoginForm
from recipehub import mongo, bcrypt
from recipehub.models import User
from bson.objectid import ObjectId

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = {
            "username": form.username.data,
            "email": form.email.data,
            "password": hashed_password
        }
        mongo.db.users.insert_one(user)
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    
    # Debugging statement
    print("Form Submitted: ", form.validate_on_submit())
    
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"username": form.username.data})
        
        # Debugging statement
        print("User Found: ", user)
        
        if user and bcrypt.check_password_hash(user["password"], form.password.data):
            user_obj = User(str(user["_id"]), user["username"])
            login_user(user_obj, remember=form.remember.data)
            return redirect(url_for('main.index'))
        else:
            flash('Login unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
