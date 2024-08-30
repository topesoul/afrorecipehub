import os
import uuid
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, session,
    current_app
)
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from recipehub.forms import RegistrationForm, LoginForm, ChangeUsernameForm
from recipehub import mongo, bcrypt
from recipehub.models import User
from bson.objectid import ObjectId


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('main.index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        existing_user = mongo.db.users.find_one({
            "$or": [{"email": form.email.data}, {"username": username}]
        })
        if existing_user:
            flash(
                'Username or email is already taken. Please try another.',
                'danger'
            )
            return render_template('register.html', form=form)

        hashed_password = bcrypt.generate_password_hash(
            form.password.data
        ).decode('utf-8')
        user = {
            "username": username,
            "email": form.email.data,
            "password": hashed_password,
            "isAdmin": False,
            "profile_image": "images/user-image.jpg"
        }
        mongo.db.users.insert_one(user)
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        user = mongo.db.users.find_one({"username": username})
        if user and bcrypt.check_password_hash(
            user["password"], form.password.data
        ):
            profile_image = user.get(
                "profile_image", "images/user-image.jpg"
            )
            user_obj = User(
                str(user["_id"]), user["username"], profile_image
            )
            login_user(user_obj, remember=form.remember.data)
            session['is_admin'] = user.get('isAdmin', False)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash(
                'Login unsuccessful. Please check username and password.',
                'danger'
            )

    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('is_admin', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/change_username/<username>', methods=['GET', 'POST'])
@login_required
def change_username(username):
    """
    Allow authenticated users to change their username.
    The new username is validated to ensure it is not
    the same as the current username or already taken
    by another user. Contextual feedback is provided
    to guide the user.
    """
    if username.lower() != current_user.username.lower():
        flash('You cannot change another user\'s username!', 'danger')
        return redirect(url_for('main.index'))

    form = ChangeUsernameForm()

    if form.validate_on_submit():
        new_username = form.username.data.strip().lower()

        # Validate the new username against the current user
        try:
            form.validate_username(form.username, current_user=current_user)
        except ValidationError as e:
            flash(str(e), 'warning')
            return render_template('change_username.html', form=form)

        # If no errors, proceed with updating the username
        mongo.db.users.update_one(
            {"_id": ObjectId(current_user.get_id())},
            {"$set": {"username": new_username}}
        )
        flash('Your username has been updated!', 'success')
        return redirect(url_for('main.dashboard', username=new_username))

    elif form.errors:
        for field, error_messages in form.errors.items():
            for error in error_messages:
                flash(error, 'danger')

    return render_template('change_username.html', form=form)


@auth_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    profile_image = request.files.get('profile_image')
    remove_image = request.form.get('remove_image')

    if profile_image and profile_image.filename:
        filename = secure_filename(
            str(uuid.uuid4()) + "_" + profile_image.filename
        )
        upload_folder = os.path.join(
            current_app.root_path, 'static', 'uploads', 'profile_images'
        )
        image_path = os.path.join(upload_folder, filename)

        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        profile_image.save(image_path)
        image_path_relative = os.path.join(
            'uploads', 'profile_images', filename
        )

        current_image_path = current_user.profile_image
        if current_image_path != "images/user-image.jpg":
            try:
                os.remove(os.path.join(
                    current_app.root_path, 'static', current_image_path
                ))
            except Exception as e:
                pass

        mongo.db.users.update_one(
            {"_id": ObjectId(current_user.get_id())},
            {"$set": {"profile_image": image_path_relative}}
        )

        flash('Profile updated successfully.', 'success')

    elif remove_image:
        current_image_path = current_user.profile_image
        if current_image_path != "images/user-image.jpg":
            try:
                os.remove(os.path.join(
                    current_app.root_path, 'static', current_image_path
                ))
            except Exception as e:
                pass

        mongo.db.users.update_one(
            {"_id": ObjectId(current_user.get_id())},
            {"$set": {"profile_image": "images/user-image.jpg"}}
        )

        flash('Profile image removed and reverted to default.', 'success')

    else:
        flash('No image selected or image upload failed.', 'warning')

    user = mongo.db.users.find_one({"_id": ObjectId(current_user.get_id())})
    login_user(User(
        str(user["_id"]), user["username"],
        user.get("profile_image", "images/user-image.jpg")
    ))

    return redirect(url_for('main.dashboard', username=current_user.username))


@auth_bp.route('/delete_account/<username>', methods=['POST'])
@login_required
def delete_account(username):
    if username != current_user.username and not session.get('is_admin'):
        flash('You cannot delete another user\'s account!', 'danger')
        return redirect(url_for('main.index'))

    user = mongo.db.users.find_one({"_id": ObjectId(current_user.get_id())})

    if user["profile_image"] != "images/user-image.jpg":
        try:
            os.remove(os.path.join(
                current_app.root_path, 'static', user["profile_image"]
            ))
        except Exception as e:
            pass

    mongo.db.users.delete_one({"_id": ObjectId(current_user.get_id())})
    logout_user()
    flash('Your account has been deleted!', 'success')
    return redirect(url_for('main.index'))
