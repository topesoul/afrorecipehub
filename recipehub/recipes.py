from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from recipehub.forms import RecipeForm, CommentForm
from recipehub import mongo
from bson.objectid import ObjectId
from datetime import datetime

recipes_bp = Blueprint('recipes', __name__)

@recipes_bp.route('/get_recipes')
def get_recipes():
    recipes = mongo.db.recipes.find()
    categories = mongo.db.categories.find()
    return render_template('recipes.html', recipes=recipes, categories=categories)

@recipes_bp.route('/new_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    form = RecipeForm()
    form.category.choices = [(str(category["_id"]), category["name"]) for category in mongo.db.categories.find()]
    if form.validate_on_submit():
        recipe = {
            "title": form.title.data,
            "ingredients": form.ingredients.data,
            "instructions": form.instructions.data,
            "category_id": ObjectId(form.category.data),
            "created_by": ObjectId(current_user.get_id()),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        mongo.db.recipes.insert_one(recipe)
        flash('Recipe added!', 'success')
        return redirect(url_for('recipes.get_recipes'))
    return render_template('new_recipe.html', form=form)

@recipes_bp.route('/edit_recipe/<recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    form = RecipeForm(obj=recipe)
    form.category.choices = [(str(category["_id"]), category["name"]) for category in mongo.db.categories.find()]
    if form.validate_on_submit():
        mongo.db.recipes.update_one({"_id": ObjectId(recipe_id)}, {
            "$set": {
                "title": form.title.data,
                "ingredients": form.ingredients.data,
                "instructions": form.instructions.data,
                "category_id": ObjectId(form.category.data),
                "updated_at": datetime.utcnow()
            }
        })
        flash('Recipe updated!', 'success')
        return redirect(url_for('recipes.get_recipes'))
    return render_template('edit_recipe.html', form=form, recipe=recipe)

@recipes_bp.route('/delete_recipe/<recipe_id>')
@login_required
def delete_recipe(recipe_id):
    mongo.db.recipes.delete_one({"_id": ObjectId(recipe_id)})
    flash('Recipe deleted!', 'success')
    return redirect(url_for('recipes.get_recipes'))

@recipes_bp.route('/recipe/<recipe_id>', methods=['GET', 'POST'])
def view_recipe(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
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
