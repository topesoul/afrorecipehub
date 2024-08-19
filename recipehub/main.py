from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from recipehub.forms import ProfileUpdateForm
from recipehub import mongo
from bson.objectid import ObjectId

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html')

@bp.route('/about')
def about():
    return render_template('about.html')

@bp.route('/dashboard/<username>', methods=['GET', 'POST'])
@login_required
def dashboard(username):
    if username != current_user.username:
        return redirect(url_for('main.index'))
    
    form = ProfileUpdateForm()
    
    # Fetch user's recipes
    recipes = list(mongo.db.recipes.find({"created_by": ObjectId(current_user.get_id())}))
    
    if form.validate_on_submit():
        update_data = {"username": form.username.data}
        
        profile_image = form.profile_image.data
        if profile_image:
            filename = secure_filename(profile_image.filename)
            image_path = os.path.join('static/uploads', filename)
            
            if not os.path.exists('static/uploads'):
                os.makedirs('static/uploads')
            
            profile_image.save(image_path)
            update_data["profile_image"] = image_path
        
        mongo.db.users.update_one(
            {"_id": ObjectId(current_user.get_id())},
            {"$set": update_data}
        )
        
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('main.dashboard', username=current_user.username))
    
    return render_template('dashboard.html', username=username, recipes=recipes, form=form)