from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from recipehub.forms import RegistrationForm, LoginForm, ChangeUsernameForm
from recipehub import mongo, bcrypt
from recipehub.models import User
from bson.objectid import ObjectId
import os

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
            "password": hashed_password,
            "isAdmin": False,  # Default to non-admin user
            "profile_image": "images/user-image.jpg"  # Default profile image
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
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"username": form.username.data})
        if user and bcrypt.check_password_hash(user["password"], form.password.data):
            user_obj = User(str(user["_id"]), user["username"], user.get("profile_image"))
            login_user(user_obj, remember=form.remember.data)
            session['is_admin'] = user.get('isAdmin', False)
            return redirect(url_for('main.index'))
        else:
            flash('Login unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('is_admin', None)
    return redirect(url_for('main.index'))

@auth_bp.route('/change_username/<username>', methods=['GET', 'POST'])
@login_required
def change_username(username):
    if username != current_user.username:
        flash('You cannot change another user\'s username!', 'danger')
        return redirect(url_for('main.index'))
    
    form = ChangeUsernameForm()
    if form.validate_on_submit():
        mongo.db.users.update_one(
            {"_id": ObjectId(current_user.get_id())},
            {"$set": {"username": form.username.data}}
        )
        flash('Your username has been updated!', 'success')
        return redirect(url_for('main.dashboard', username=form.username.data))
    
    return render_template('change_username.html', form=form)

@auth_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    profile_image = request.files.get('profile_image')

    update_data = {}

    if profile_image:
        filename = secure_filename(profile_image.filename)
        image_path = os.path.join('static/uploads', filename)
        
        if not os.path.exists('static/uploads'):
            os.makedirs('static/uploads')
        
        profile_image.save(image_path)
        update_data['profile_image'] = image_path

    mongo.db.users.update_one(
        {"_id": ObjectId(current_user.get_id())},
        {"$set": update_data}
    )
    
    flash('Profile updated successfully', 'success')
    return redirect(url_for('main.dashboard'))

@auth_bp.route('/delete_account/<username>', methods=['POST'])
@login_required
def delete_account(username):
    if username != current_user.username and not session.get('is_admin'):
        flash('You cannot delete another user\'s account!', 'danger')
        return redirect(url_for('main.index'))
    
    mongo.db.users.delete_one({"_id": ObjectId(current_user.get_id())})
    logout_user()
    flash('Your account has been deleted!', 'success')
    return redirect(url_for('main.index'))
