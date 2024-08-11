from flask import render_template, redirect, url_for, request, flash
from recipehub import app, mongo, bcrypt
from recipehub.forms import RegistrationForm, LoginForm, RecipeForm, CommentForm
from flask_login import login_user, current_user, logout_user, login_required
from bson.objectid import ObjectId
from datetime import datetime

@app.route('/')
@app.route('/get_recipes')
def get_recipes():
    print("Fetching recipes from the database...")
    recipes = mongo.db.recipes.find()
    print(f"Fetched {recipes.count()} recipes")
    categories = mongo.db.categories.find()
    return render_template('recipes.html', recipes=recipes, categories=categories)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        print("Registering new user...")
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = {
            "username": form.username.data,
            "email": form.email.data,
            "password": hashed_password
        }
        mongo.db.users.insert_one(user)
        print(f"User {form.username.data} registered successfully.")
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print(f"Attempting to log in user {form.email.data}...")
        user = mongo.db.users.find_one({"email": form.email.data})
        if user and bcrypt.check_password_hash(user["password"], form.password.data):
            login_user(User(user["_id"], user["username"]))
            print(f"User {form.email.data} logged in successfully.")
            return redirect(url_for('get_recipes'))
        else:
            print(f"Login failed for user {form.email.data}.")
            flash('Login unsuccessful. Please check your email and password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    print(f"User {current_user.username} logging out...")
    logout_user()
    return redirect(url_for('get_recipes'))

@app.route('/new_recipe', methods=['GET', 'POST'])
@login_required
def new_recipe():
    form = RecipeForm()
    form.category.choices = [(str(category["_id"]), category["name"]) for category in mongo.db.categories.find()]
    if form.validate_on_submit():
        print("Adding a new recipe...")
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
        print(f"Recipe {form.title.data} added successfully.")
        flash('Recipe added!', 'success')
        return redirect(url_for('get_recipes'))
    return render_template('new_recipe.html', form=form)

@app.route('/edit_recipe/<recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    print(f"Editing recipe with ID {recipe_id}...")
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    form = RecipeForm(obj=recipe)
    form.category.choices = [(str(category["_id"]), category["name"]) for category in mongo.db.categories.find()]
    if form.validate_on_submit():
        print("Updating recipe...")
        mongo.db.recipes.update_one({"_id": ObjectId(recipe_id)}, {
            "$set": {
                "title": form.title.data,
                "ingredients": form.ingredients.data,
                "instructions": form.instructions.data,
                "category_id": ObjectId(form.category.data),
                "updated_at": datetime.utcnow()
            }
        })
        print(f"Recipe {form.title.data} updated successfully.")
        flash('Recipe updated!', 'success')
        return redirect(url_for('get_recipes'))
    return render_template('edit_recipe.html', form=form, recipe=recipe)

@app.route('/delete_recipe/<recipe_id>')
@login_required
def delete_recipe(recipe_id):
    print(f"Deleting recipe with ID {recipe_id}...")
    mongo.db.recipes.delete_one({"_id": ObjectId(recipe_id)})
    print(f"Recipe with ID {recipe_id} deleted successfully.")
    flash('Recipe deleted!', 'success')
    return redirect(url_for('get_recipes'))

@app.route('/profile')
@login_required
def profile():
    print(f"Fetching profile for user {current_user.username}...")
    recipes = mongo.db.recipes.find({"created_by": ObjectId(current_user.get_id())})
    return render_template('profile.html', recipes=recipes)

@app.route('/recipe/<recipe_id>', methods=['GET', 'POST'])
def view_recipe(recipe_id):
    print(f"Viewing recipe with ID {recipe_id}...")
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    comments = mongo.db.comments.find({"recipe_id": ObjectId(recipe_id)})
    form = CommentForm()
    if form.validate_on_submit():
        print(f"Adding comment to recipe with ID {recipe_id}...")
        comment = {
            "recipe_id": ObjectId(recipe_id),
            "user_id": ObjectId(current_user.get_id()),
            "comment": form.comment.data,
            "created_at": datetime.utcnow()
        }
        mongo.db.comments.insert_one(comment)
        print("Comment added successfully.")
        flash('Comment added!', 'success')
        return redirect(url_for('view_recipe', recipe_id=recipe_id))
    return render_template('view_recipe.html', recipe=recipe, comments=comments, form=form)
