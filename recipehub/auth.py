import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from recipehub.forms import RegistrationForm, LoginForm, ChangeUsernameForm
from recipehub import mongo, bcrypt
from recipehub.models import User
from bson.objectid import ObjectId

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles user registration. If the user is already authenticated, redirect to the main page.
    On form submission, creates a new user in the database and redirects to the login page.
    """
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        existing_user = mongo.db.users.find_one({"$or": [{"email": form.email.data}, {"username": form.username.data}]})
        if existing_user:
            flash('Username or email is already taken. Please try another.', 'danger')
            return render_template('register.html', form=form)

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = {
            "username": form.username.data,
            "email": form.email.data,
            "password": hashed_password,
            "isAdmin": False,  # Default to non-admin user
            "profile_image": "images/user-image.jpg"  # Default profile image path
        }
        mongo.db.users.insert_one(user)
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login. If the user is already authenticated, redirect to the main page.
    On form submission, validates user credentials and logs in the user.
    """
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"username": form.username.data})
        if user and bcrypt.check_password_hash(user["password"], form.password.data):
            profile_image = user.get("profile_image", "images/user-image.jpg")  # Correct default path
            user_obj = User(str(user["_id"]), user["username"], profile_image)
            login_user(user_obj, remember=form.remember.data)
            session['is_admin'] = user.get('isAdmin', False)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Login unsuccessful. Please check username and password.', 'danger')
    
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """
    Logs out the user and clears the session. Redirects to the main page.
    """
    logout_user()
    session.pop('is_admin', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/change_username/<username>', methods=['GET', 'POST'])
@login_required
def change_username(username):
    """
    Allows the authenticated user to change their username.
    If the username is already taken, prompts the user to choose a different one.
    """
    if username != current_user.username:
        flash('You cannot change another user\'s username!', 'danger')
        return redirect(url_for('main.index'))
    
    form = ChangeUsernameForm(username=current_user.username)
    
    if form.validate_on_submit():
        new_username = form.username.data
        
        if new_username == current_user.username:
            flash('This is already your username. Please choose a different one.', 'warning')
            return redirect(url_for('auth.change_username', username=current_user.username))
        
        existing_user = mongo.db.users.find_one({"username": new_username})
        
        if existing_user:
            flash('That username is taken. Please choose a different one.', 'danger')
        else:
            mongo.db.users.update_one(
                {"_id": ObjectId(current_user.get_id())},
                {"$set": {"username": new_username}}
            )
            flash('Your username has been updated!', 'success')
            return redirect(url_for('main.dashboard', username=new_username))
    
    return render_template('change_username.html', form=form)

@auth_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    """
    Allows the authenticated user to update their profile image or revert to default if the image is removed.
    """
    profile_image = request.files.get('profile_image')
    remove_image = request.form.get('remove_image')

    if profile_image and profile_image.filename:
        # Handle profile image upload
        filename = secure_filename(str(uuid.uuid4()) + "_" + profile_image.filename)
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profile_images')
        image_path = os.path.join(upload_folder, filename)
        
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        profile_image.save(image_path)
        
        # Store the relative path in the database
        image_path_relative = os.path.join('uploads', 'profile_images', filename)
        
        # Remove the old image if not default
        current_image_path = current_user.profile_image
        if current_image_path != "images/user-image.jpg":  # Update condition to correct default path
            try:
                os.remove(os.path.join(current_app.root_path, 'static', current_image_path))
            except Exception as e:
                pass  # If there is an error deleting the old image, just ignore it
        
        mongo.db.users.update_one(
            {"_id": ObjectId(current_user.get_id())},
            {"$set": {"profile_image": image_path_relative}}
        )
        
        flash('Profile updated successfully.', 'success')

    elif remove_image:
        # Handle removal of profile image (set to default)
        current_image_path = current_user.profile_image
        if current_image_path != "images/user-image.jpg":  # Update condition to correct default path
            try:
                os.remove(os.path.join(current_app.root_path, 'static', current_image_path))
            except Exception as e:
                pass  # If there is an error deleting the old image, just ignore it
        
        mongo.db.users.update_one(
            {"_id": ObjectId(current_user.get_id())},
            {"$set": {"profile_image": "images/user-image.jpg"}}  # Update to correct default path
        )
        
        flash('Profile image removed and reverted to default.', 'success')

    else:
        flash('No image selected or image upload failed.', 'warning')
    
    # Update the user's session to reflect the new image path
    user = mongo.db.users.find_one({"_id": ObjectId(current_user.get_id())})
    login_user(User(str(user["_id"]), user["username"], user.get("profile_image", "images/user-image.jpg")))  # Correct default path
    
    return redirect(url_for('main.dashboard', username=current_user.username))

@auth_bp.route('/delete_account/<username>', methods=['POST'])
@login_required
def delete_account(username):
    """
    Allows the authenticated user to delete their account.
    Admins can also delete other users' accounts.
    """
    if username != current_user.username and not session.get('is_admin'):
        flash('You cannot delete another user\'s account!', 'danger')
        return redirect(url_for('main.index'))
    
    # Fetch the current user's data
    user = mongo.db.users.find_one({"_id": ObjectId(current_user.get_id())})
    
    # Remove profile image if it's not the default one
    if user["profile_image"] != "images/user-image.jpg":  # Update condition to correct default path
        try:
            os.remove(os.path.join(current_app.root_path, 'static', user["profile_image"]))
        except Exception as e:
            pass  # If there is an error deleting the old image, just ignore it
    
    mongo.db.users.delete_one({"_id": ObjectId(current_user.get_id())})
    logout_user()
    flash('Your account has been deleted!', 'success')
    return redirect(url_for('main.index'))