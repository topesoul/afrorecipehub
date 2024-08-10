from flask import render_template, redirect, url_for, request, flash
from recipehub import app, mongo, bcrypt
from recipehub.models import RegistrationForm, LoginForm, RecipeForm, CommentForm, User
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime

# Route to view all recipes
@app.route('/')
@app.route('/get_recipes')
def get_recipes():
    recipes = mongo.db.recipes.find()
    categories = mongo.db.categories.find()
    return render_template('recipes.html', recipes=recipes, categories=categories)

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = {
            "username": form.username.data,
            "email": form.email.data,
            "password": hashed_password,
            "created_at": datetime.utcnow()
        }
        mongo.db.users.insert_one(user)
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"email": form.email.data})
        if user and bcrypt.check_password_hash(user["password"], form.password.data):
            login_user(User(str(user["_id"]), user["username"]))
            flash('Login successful', 'success')
            return redirect(url_for('get_recipes'))
        else:
            flash('Login unsuccessful. Please check your email and password', 'danger')
    return render_template('login.html', form=form)

# Route for user logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('get_recipes'))

# Route to add a new recipe
@app.route('/new_recipe', methods=['GET', 'POST'])
@login_required
def new_recipe():
    form = RecipeForm()
    form.category.choices = [(str(category["_id"]), category["name"]) for category in mongo.db.categories.find()]
    if form.validate_on_submit():
        recipe = {
            "title": form.title.data,
            "ingredients": form.ingredients.data,
            "instructions": form.instructions.data,
            "category_id": form.category.data,
            "created_by": current_user.id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        mongo.db.recipes.insert_one(recipe)
        flash('Recipe added!', 'success')
        return redirect(url_for('get_recipes'))
    return render_template('new_recipe.html', form=form)

# Route to edit an existing recipe
@app.route('/edit_recipe/<recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": recipe_id})
    if not recipe:
        flash('Recipe not found', 'danger')
        return redirect(url_for('get_recipes'))
    
    form = RecipeForm(obj=recipe)
    form.category.choices = [(str(category["_id"]), category["name"]) for category in mongo.db.categories.find()]
    if form.validate_on_submit():
        updated_data = {
            "title": form.title.data,
            "ingredients": form.ingredients.data,
            "instructions": form.instructions.data,
            "category_id": form.category.data,
            "updated_at": datetime.utcnow()
        }
        mongo.db.recipes.update_one({"_id": recipe_id}, {"$set": updated_data})
        flash('Recipe updated!', 'success')
        return redirect(url_for('get_recipes'))
    return render_template('edit_recipe.html', form=form, recipe=recipe)

# Route to delete a recipe
@app.route('/delete_recipe/<recipe_id>')
@login_required
def delete_recipe(recipe_id):
    mongo.db.recipes.delete_one({"_id": recipe_id})
    flash('Recipe deleted!', 'success')
    return redirect(url_for('get_recipes'))

# Route to view the user's profile and their recipes
@app.route('/profile')
@login_required
def profile():
    recipes = mongo.db.recipes.find({"created_by": current_user.id})
    return render_template('profile.html', recipes=recipes)

# Route to view a specific recipe and its comments
@app.route('/recipe/<recipe_id>', methods=['GET', 'POST'])
def view_recipe(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": recipe_id})
    if not recipe:
        flash('Recipe not found', 'danger')
        return redirect(url_for('get_recipes'))

    comments = mongo.db.comments.find({"recipe_id": recipe_id})
    form = CommentForm()
    if form.validate_on_submit():
        comment = {
            "recipe_id": recipe_id,
            "user_id": current_user.id,
            "comment": form.comment.data,
            "created_at": datetime.utcnow()
        }
        mongo.db.comments.insert_one(comment)
        flash('Comment added!', 'success')
        return redirect(url_for('view_recipe', recipe_id=recipe_id))
    return render_template('view_recipe.html', recipe=recipe, comments=comments, form=form)

# Custom 404 error page
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

# Custom 500 error page
@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500