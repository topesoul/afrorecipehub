from flask import flash, render_template, redirect, request, url_for
from flask_login import login_user, current_user, logout_user, login_required
from recipehub import app, mongo, bcrypt
from bson.objectid import ObjectId
from recipehub.forms import RegistrationForm, LoginForm, RecipeForm
from recipehub.models import User, Recipe

@app.route("/")
@app.route("/get_recipes")
def get_recipes():
    recipes = Recipe.objects.all()
    return render_template("recipes.html", recipes=recipes)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        user.save()
        flash("Registration successful!", "success")
        return redirect(url_for('login'))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('profile'))
        else:
            flash("Login failed. Check your username and/or password", "danger")
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route("/new_recipe", methods=["GET", "POST"])
@login_required
def new_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        recipe = Recipe(
            name=form.name.data,
            ingredients=form.ingredients.data,
            instructions=form.instructions.data,
            created_by=current_user._get_current_object()
        )
        recipe.save()
        flash("Recipe added successfully!", "success")
        return redirect(url_for('get_recipes'))
    return render_template("new_recipe.html", form=form)

@app.route("/edit_recipe/<recipe_id>", methods=["GET", "POST"])
@login_required
def edit_recipe(recipe_id):
    recipe = Recipe.objects.get_or_404(id=ObjectId(recipe_id))
    form = RecipeForm(obj=recipe)
    if form.validate_on_submit():
        recipe.update(
            name=form.name.data,
            ingredients=form.ingredients.data,
            instructions=form.instructions.data
        )
        flash("Recipe updated successfully!", "success")
        return redirect(url_for('get_recipes'))
    return render_template("edit_recipe.html", form=form, recipe=recipe)

@app.route("/delete_recipe/<recipe_id>")
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.objects.get_or_404(id=ObjectId(recipe_id))
    recipe.delete()
    flash("Recipe deleted successfully.", "success")
    return redirect(url_for('get_recipes'))

@app.route("/profile")
@login_required
def profile():
    recipes = Recipe.objects(created_by=current_user._get_current_object())
    return render_template("profile.html", recipes=recipes)
