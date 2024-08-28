import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from recipehub.forms import ProfileUpdateForm
from recipehub import mongo
from bson.objectid import ObjectId


# Blueprint for the main routes
bp = Blueprint('main', __name__)


@bp.route('/')
@bp.route('/index')
def index():
    """
    Route to serve the homepage.
    """
    return render_template('index.html')


@bp.route('/dashboard/<username>', methods=['GET', 'POST'])
@login_required
def dashboard(username):
    """
    User dashboard that allows profile updates and displays the user's recipes.
    Access restricted to the logged-in user
    whose username matches the URL parameter.
    """
    # Ensure the user can only access their own dashboard
    if username != current_user.username:
        flash('You can only access your own dashboard.', 'danger')
        return redirect(url_for('main.index'))

    form = ProfileUpdateForm()

    # Fetch the user's recipes from the database
    recipes = list(
        mongo.db.recipes.find(
            {"created_by": ObjectId(current_user.get_id())}
        )
    )

    if form.validate_on_submit():
        update_data = {"username": form.username.data.strip()}

        # Handle profile image upload
        profile_image = form.profile_image.data
        if profile_image:
            filename = secure_filename(profile_image.filename)
            upload_folder = os.path.join('static/uploads', 'profile_images')
            image_path = os.path.join(upload_folder, filename)

            # Create the directory if it does not exist
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            # Save the uploaded profile image
            profile_image.save(image_path)
            update_data["profile_image"] = os.path.join(
                'uploads/profile_images', filename
            )

        try:
            # Update the user's profile data in MongoDB
            mongo.db.users.update_one(
                {"_id": ObjectId(current_user.get_id())},
                {"$set": update_data}
            )
            flash('Your profile has been updated!', 'success')
        except Exception as e:
            # Handle potential database errors
            flash(
                f"An error occurred while updating your profile: {e}", 'danger'
            )

        return redirect(
            url_for('main.dashboard', username=current_user.username)
        )

    # Render the dashboard template with the current user's data
    return render_template(
        'dashboard.html', username=username, recipes=recipes, form=form
    )
