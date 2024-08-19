import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from recipehub.forms import RecipeForm, CommentForm, BookmarkForm
from recipehub import mongo
from bson.objectid import ObjectId
from datetime import datetime

recipes_bp = Blueprint('recipes', __name__)

DEFAULT_IMAGE_PATH = 'images/default_recipe_image.jpg'

@recipes_bp.route('/get_recipes')
def get_recipes():
    # Track unique visitors
    if not session.get('has_visited'):
        session['has_visited'] = True
        mongo.db.site_stats.update_one({}, {"$inc": {"unique_visitors": 1}}, upsert=True)
    
    # Retrieve and display unique visitor count
    site_stats = mongo.db.site_stats.find_one() or {}
    unique_visitors = site_stats.get('unique_visitors', 0)

    recipes = list(mongo.db.recipes.find())
    categories = list(mongo.db.categories.find())
    category_list = [(str(category["_id"]), category["name"]) for category in categories]
    
    user_bookmarks = []
    if current_user.is_authenticated:
        user = mongo.db.users.find_one({"_id": ObjectId(current_user.get_id())})
        if user and 'bookmarked_recipes' in user:
            user_bookmarks = user['bookmarked_recipes']

    for recipe in recipes:
        recipe['category_name'] = next((cat['name'] for cat in categories if cat['_id'] == recipe['category_id']), "Unknown")
        recipe['comment_count'] = mongo.db.comments.count_documents({"recipe_id": recipe["_id"]})
        # Check if the recipe is bookmarked by the user
        recipe['is_bookmarked'] = recipe['_id'] in user_bookmarks
    
    bookmark_form = BookmarkForm()  # Initialize the bookmark form

    return render_template('recipes.html', recipes=recipes, categories=category_list, unique_visitors=unique_visitors, form=bookmark_form)

@recipes_bp.route('/new_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    form = RecipeForm()
    form.category.choices = [(str(category["_id"]), category["name"]) for category in mongo.db.categories.find()]
    
    if form.validate_on_submit():
        image_file = request.files['image']
        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'recipes')
            image_path = os.path.join(upload_folder, filename)
            
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            image_file.save(image_path)
            image_path = os.path.join('uploads', 'recipes', filename)
        else:
            image_path = DEFAULT_IMAGE_PATH
        
        recipe = {
            "title": form.title.data,
            "description": form.description.data,
            "ingredients": form.ingredients.data.splitlines(),
            "instructions": form.instructions.data,
            "category_id": ObjectId(form.category.data),
            "created_by": ObjectId(current_user.get_id()),
            "image_path": image_path,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        mongo.db.recipes.insert_one(recipe)
        
        # Increment user's points
        mongo.db.users.update_one(
            {"_id": ObjectId(current_user.get_id())},
            {"$inc": {"points": 10}}
        )

        flash('Recipe added! You earned 10 points.', 'success')
        return redirect(url_for('recipes.get_recipes'))
    
    return render_template('add_recipe.html', form=form)

@recipes_bp.route('/edit_recipe/<recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    if not recipe:
        flash('Recipe not found.', 'danger')
        return redirect(url_for('recipes.get_recipes'))
    
    # Check if the current user is the creator of the recipe or an admin
    if str(recipe['created_by']) != current_user.get_id() and not session.get('is_admin'):
        flash('You do not have permission to edit this recipe.', 'danger')
        return redirect(url_for('recipes.get_recipes'))

    form = RecipeForm(obj=recipe)
    form.category.choices = [(str(category["_id"]), category["name"]) for category in mongo.db.categories.find()]
    
    if form.validate_on_submit():
        update_data = {
            "title": form.title.data,
            "description": form.description.data,
            "ingredients": form.ingredients.data.splitlines(),
            "instructions": form.instructions.data,
            "category_id": ObjectId(form.category.data),
            "updated_at": datetime.utcnow()
        }
        
        if form.remove_image.data:
            update_data["image_path"] = DEFAULT_IMAGE_PATH
        elif request.files['image'] and request.files['image'].filename != '':
            image_file = request.files['image']
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'recipes')
            image_path = os.path.join(upload_folder, filename)
            
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            image_file.save(image_path)
            update_data["image_path"] = os.path.join('uploads', 'recipes', filename)
        
        mongo.db.recipes.update_one({"_id": ObjectId(recipe_id)}, {"$set": update_data})
        flash('Recipe updated!', 'success')
        return redirect(url_for('recipes.view_recipe', recipe_id=recipe_id))
    
    return render_template('edit_recipe.html', form=form, recipe=recipe)

@recipes_bp.route('/delete_recipe/<recipe_id>')
@login_required
def delete_recipe(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    if recipe and (recipe['created_by'] == ObjectId(current_user.get_id()) or session.get('is_admin')):
        if recipe["image_path"] != DEFAULT_IMAGE_PATH:
            try:
                os.remove(os.path.join(current_app.root_path, 'static', recipe["image_path"]))
            except Exception as e:
                flash(f"Error removing old image: {e}", 'danger')
        
        mongo.db.recipes.delete_one({"_id": ObjectId(recipe_id)})
        
        # Decrement user's points
        mongo.db.users.update_one(
            {"_id": ObjectId(current_user.get_id())},
            {"$inc": {"points": -10}}
        )
        
        flash('Recipe deleted! 10 points deducted.', 'success')
    else:
        flash('You do not have permission to delete this recipe.', 'danger')
    return redirect(url_for('recipes.get_recipes'))

@recipes_bp.route('/recipe/<recipe_id>', methods=['GET', 'POST'])
def view_recipe(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    if not recipe:
        return render_template('404.html'), 404
    
    comments = list(mongo.db.comments.find({"recipe_id": ObjectId(recipe_id)}))
    
    form = CommentForm()
    if form.validate_on_submit():
        comment = {
            "recipe_id": ObjectId(recipe_id),
            "user_id": ObjectId(current_user.get_id()),
            "username": current_user.username,  # Store the username directly
            "comment": form.comment.data,
            "created_at": datetime.utcnow()
        }
        mongo.db.comments.insert_one(comment)
        
        # Increment the comment count in the recipe document
        mongo.db.recipes.update_one(
            {"_id": ObjectId(recipe_id)},
            {"$inc": {"comment_count": 1}}
        )
        
        # Increment user's points
        mongo.db.users.update_one(
            {"_id": ObjectId(current_user.get_id())},
            {"$inc": {"points": 2}}
        )
        
        flash('Comment added! You earned 2 points.', 'success')
        return redirect(url_for('recipes.view_recipe', recipe_id=recipe_id))
    
    # Check if the current user has bookmarked the recipe
    is_bookmarked = False
    if current_user.is_authenticated:
        user = mongo.db.users.find_one({"_id": ObjectId(current_user.get_id())})
        if user and 'bookmarked_recipes' in user and ObjectId(recipe_id) in user['bookmarked_recipes']:
            is_bookmarked = True

    bookmark_form = BookmarkForm()  # Initialize the bookmark form

    return render_template('view_recipe.html', recipe=recipe, comments=comments, form=form, bookmark_form=bookmark_form, is_bookmarked=is_bookmarked)

@recipes_bp.route('/bookmark/<recipe_id>', methods=['POST'])
@login_required
def toggle_bookmark(recipe_id):
    user_id = current_user.get_id()
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    
    if ObjectId(recipe_id) in user.get('bookmarked_recipes', []):
        # If recipe is already bookmarked, remove it
        mongo.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$pull": {"bookmarked_recipes": ObjectId(recipe_id)}}
        )
        flash('Recipe unbookmarked!', 'success')
    else:
        # If recipe is not bookmarked, add it
        mongo.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$addToSet": {"bookmarked_recipes": ObjectId(recipe_id)}}
        )
        flash('Recipe bookmarked!', 'success')
    
    return redirect(url_for('recipes.view_recipe', recipe_id=recipe_id))

@recipes_bp.route('/bookmarks')
@login_required
def view_bookmarks():
    user = mongo.db.users.find_one({"_id": ObjectId(current_user.get_id())})
    bookmarked_recipes = list(mongo.db.recipes.find({"_id": {"$in": user.get('bookmarked_recipes', [])}}))
    return render_template('bookmarked_recipes.html', recipes=bookmarked_recipes)