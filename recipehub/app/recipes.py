from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from app import mongo

recipes = Blueprint('recipes', __name__)

@recipes.route('/new_recipe', methods=['GET', 'POST'])
@login_required
def new_recipe():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        ingredients = request.form.get('ingredients')
        instructions = request.form.get('instructions')

        recipe = {
            'title': title,
            'description': description,
            'ingredients': ingredients,
            'instructions': instructions,
            'author_id': current_user.id
        }

        mongo.db.recipes.insert_one(recipe)
        return redirect(url_for('main.profile'))

    return render_template('new_recipe.html')

@recipes.route('/edit_recipe/<id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(id):
    recipe = mongo.db.recipes.find_one_or_404({'_id': ObjectId(id)})

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        ingredients = request.form.get('ingredients')
        instructions = request.form.get('instructions')

        mongo.db.recipes.update_one({'_id': ObjectId(id)}, {'$set': {
            'title': title,
            'description': description,
            'ingredients': ingredients,
            'instructions': instructions
        }})

        return redirect(url_for('main.profile'))

    return render_template('edit_recipe.html', recipe=recipe)

@recipes.route('/delete_recipe/<id>', methods=['DELETE'])
@login_required
def delete_recipe(id):
    mongo.db.recipes.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('main.profile'))
