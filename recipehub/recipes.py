import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from recipehub.forms import RecipeForm, CommentForm
from recipehub import mongo
from bson.objectid import ObjectId
from datetime import datetime

recipes_bp = Blueprint('recipes', __name__)

DEFAULT_IMAGE_PATH = 'images/default_recipe_image.jpg'

@recipes_bp.route('/get_recipes')
def get_recipes():
    recipes = list(mongo.db.recipes.find())
    categories = list(mongo.db.categories.find())
    category_list = [(str(category["_id"]), category["name"]) for category in categories]
    
    # Add category names to each recipe for display
    for recipe in recipes:
        recipe['category_name'] = next((cat['name'] for cat in categories if cat['_id'] == recipe['category_id']), "Unknown")
    
    return render_template('recipes.html', recipes=recipes, categories=category_list)

@recipes_bp.route('/new_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    form = RecipeForm()
    form.category.choices = [(str(category["_id"]), category["name"]) for category in mongo.db.categories.find()]
    
    if form.validate_on_submit():
        # Handle image upload
        image_file = request.files['image']
        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'recipes')
            image_path = os.path.join(upload_folder, filename)
            
            # Create directory if it doesn't exist
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            # Save the image file
            try:
                image_file.save(image_path)
                # Convert to relative path for serving
                image_path = os.path.join('uploads', 'recipes', filename)
            except Exception as e:
                flash(f"Error saving image: {e}", 'danger')
                return render_template('add_recipe.html', form=form)
        else:
            image_path = DEFAULT_IMAGE_PATH  # Use default image if none is uploaded
        
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
        flash('Recipe added!', 'success')
        return redirect(url_for('recipes.get_recipes'))
    
    return render_template('add_recipe.html', form=form)

@recipes_bp.route('/edit_recipe/<recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    if not recipe:
        flash('Recipe not found.', 'danger')
        return redirect(url_for('recipes.get_recipes'))
    
    # Ensure only the creator or admin can edit the recipe
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
        
        # Handle image upload or removal
        if form.remove_image.data:
            update_data["image_path"] = DEFAULT_IMAGE_PATH
        elif request.files['image'].filename != '':
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
        flash('Recipe deleted!', 'success')
    else:
        flash('You do not have permission to delete this recipe.', 'danger')
    return redirect(url_for('recipes.get_recipes'))

@recipes_bp.route('/recipe/<recipe_id>', methods=['GET', 'POST'])
def view_recipe(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    if not recipe:
        return render_template('404.html'), 404
    
    comments = mongo.db.comments.find({"recipe_id": ObjectId(recipe_id)})
    form = CommentForm()
    if form.validate_on_submit():
        comment = {
            "recipe_id": ObjectId(recipe_id),
            "user_id": ObjectId(current_user.get_id()),
            "comment": form.comment.data,
            "created_at": datetime.utcnow()
        }
        mongo.db.comments.insert_one(comment)
        flash('Comment added!', 'success')
        return redirect(url_for('recipes.view_recipe', recipe_id=recipe_id))
    return render_template('view_recipe.html', recipe=recipe, comments=comments, form=form)