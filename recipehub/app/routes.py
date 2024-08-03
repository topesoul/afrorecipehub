from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, mongo
from app.models import User, Recipe
from app.forms import RegisterForm, LoginForm

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        mongo.db.users.insert_one({
            "username": form.username.data,
            "email": form.email.data,
            "password": hashed_password
        })
        flash('You have successfully registered!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"email": form.email.data})
        if user and check_password_hash(user['password'], form.password.data):
            login_user(User(user))
            return redirect(url_for('dashboard'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    recipes = mongo.db.recipes.find({"user_id": current_user.id})
    return render_template('dashboard.html', recipes=recipes)

@app.route('/new_recipe', methods=['GET', 'POST'])
@login_required
def new_recipe():
    if request.method == 'POST':
        mongo.db.recipes.insert_one({
            "title": request.form['title'],
            "ingredients": request.form['ingredients'],
            "instructions": request.form['instructions'],
            "category": request.form['category'],
            "user_id": current_user.id
        })
        flash('Recipe added successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('new_recipe.html')

@app.route('/edit_recipe/<recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": recipe_id})
    if request.method == 'POST':
        mongo.db.recipes.update_one({"_id": recipe_id}, {
            "$set": {
                "title": request.form['title'],
                "ingredients": request.form['ingredients'],
                "instructions": request.form['instructions'],
                "category": request.form['category']
            }
        })
        flash('Recipe updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_recipe.html', recipe=recipe)

@app.route('/delete_recipe/<recipe_id>')
@login_required
def delete_recipe(recipe_id):
    mongo.db.recipes.delete_one({"_id": recipe_id})
    flash('Recipe deleted successfully!', 'success')
    return redirect(url_for('dashboard'))
