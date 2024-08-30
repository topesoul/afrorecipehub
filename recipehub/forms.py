import os
from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SubmitField, SelectField, BooleanField,
    PasswordField, FileField
)
from wtforms.validators import (
    DataRequired, Length, Email, EqualTo, ValidationError
)
from recipehub import mongo


# =====================================
# Registration Form
# =====================================
class RegistrationForm(FlaskForm):
    """
    Form for user registration. Includes username,
    email, password, and confirmation fields.
    Validates that the username and email are unique.
    """
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=2, max=20)],
        render_kw={
            "class": "form-control",
            "placeholder": "Enter your username",
            "aria-describedby": "usernameHelp"
        }
    )
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()],
        render_kw={
            "class": "form-control",
            "placeholder": "Enter your email",
            "aria-describedby": "emailHelp"
        }
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control",
            "placeholder": "Enter your password",
            "aria-describedby": "passwordHelp"
        }
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password')],
        render_kw={
            "class": "form-control",
            "placeholder": "Re-enter your password",
            "aria-describedby": "confirmPasswordHelp"
        }
    )
    submit = SubmitField(
        'Sign Up',
        render_kw={
            "class": "btn btn-primary btn-block",
            "aria-label": "Sign up"
        }
    )

    def validate_username(self, username):
        """
        Custom validator to check if the username is already taken.
        """
        stripped_username = username.data.strip().lower()
        user = mongo.db.users.find_one({"username": stripped_username})
        if user:
            raise ValidationError(
                'That username is taken (case-insensitive). Please choose a '
                'different one.'
            )

    def validate_email(self, email):
        """
        Custom validator to check if the email is already in use.
        """
        user = mongo.db.users.find_one({"email": email.data})
        if user:
            raise ValidationError(
                'That email is already in use. Please choose a different one.'
            )


# =====================================
# Login Form
# =====================================
class LoginForm(FlaskForm):
    """
    Form for user login. Includes fields for username and password.
    """
    username = StringField(
        'Username',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control",
            "placeholder": "Enter your username",
            "aria-describedby": "usernameHelp"
        }
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control",
            "placeholder": "Enter your password",
            "aria-describedby": "passwordHelp"
        }
    )
    remember = BooleanField('Remember Me')
    submit = SubmitField(
        'Login',
        render_kw={
            "class": "btn btn-primary btn-block",
            "aria-label": "Login"
        }
    )


# =====================================
# Change Username Form
# =====================================
class ChangeUsernameForm(FlaskForm):
    """
    Form to allow users to change their username.
    Includes a custom validator to ensure the new username is not taken.
    """
    username = StringField(
        'New Username',
        validators=[DataRequired(), Length(min=2, max=20)],
        render_kw={
            "class": "form-control",
            "placeholder": "Enter your new username"
        }
    )
    submit = SubmitField(
        'Change Username',
        render_kw={
            "class": "btn btn-primary btn-block",
            "aria-label": "Change username"
        }
    )

    def validate_username(self, username, current_user=None):
        """
        Custom validator to check if the new username is already taken
        or if it's the same as the current username.
        """
        stripped_username = username.data.strip().lower()

        # Check if the new username is the same as the current one
        if current_user and stripped_username == current_user.username.lower():
            raise ValidationError(
                'This is already your username. Please choose a different one.'
            )

        # Check if the new username is taken by another user
        user = mongo.db.users.find_one({"username": stripped_username})
        if user:
            raise ValidationError(
                'That username is taken (case-insensitive). Please choose a '
                'different one.'
            )


# =====================================
# Profile Update Form
# =====================================
class ProfileUpdateForm(FlaskForm):
    """
    Form to allow users to update their profile,
    including their username and profile image.
    """
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=2, max=20)],
        render_kw={
            "class": "form-control",
            "placeholder": "Update your username"
        }
    )
    profile_image = FileField(
        'Upload Profile Image',
        render_kw={
            "class": "form-control-file",
            "aria-describedby": "profileImageHelp"
        }
    )
    submit = SubmitField(
        'Update Profile',
        render_kw={
            "class": "btn btn-primary btn-block",
            "aria-label": "Update profile"
        }
    )


# =====================================
# Recipe Form
# =====================================
class RecipeForm(FlaskForm):
    """
    Form for adding or editing a recipe.
    Includes fields for title, description, ingredients,
    instructions, category, and image.
    """
    title = StringField(
        'Recipe Title',
        validators=[DataRequired(), Length(min=2, max=100)],
        render_kw={
            "class": "form-control",
            "placeholder": "Enter the recipe title",
            "aria-describedby": "titleHelp"
        }
    )
    description = TextAreaField(
        'Description',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control",
            "placeholder": "Enter a description",
            "aria-describedby": "descriptionHelp"
        }
    )
    ingredients = TextAreaField(
        'Ingredients',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control",
            "placeholder": "List ingredients, one per line",
            "aria-describedby": "ingredientsHelp"
        }
    )
    instructions = TextAreaField(
        'Instructions',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control",
            "placeholder": "Enter the preparation steps",
            "aria-describedby": "instructionsHelp"
        }
    )
    category = SelectField(
        'Category',
        choices=[],
        validators=[DataRequired()],
        render_kw={
            "class": "form-control",
            "aria-describedby": "categoryHelp"
        }
    )
    image = FileField(
        'Upload Image',
        render_kw={
            "class": "form-control-file",
            "aria-describedby": "imageHelp"
        }
    )
    remove_image = BooleanField(
        'Remove Existing Image',
        render_kw={"class": "form-check-input"}
    )
    submit = SubmitField(
        'Save Recipe',
        render_kw={
            "class": "btn btn-primary btn-block",
            "aria-label": "Save recipe"
        }
    )

    def validate_ingredients(self, ingredients):
        """
        Custom validator to ensure that ingredients are provided
        in a valid format (one per line).
        """
        if not ingredients.data.strip():
            raise ValidationError(
                'Please provide the ingredients, each on a new line.'
            )


# =====================================
# Comment Form
# =====================================
class CommentForm(FlaskForm):
    """
    Form for adding comments to a recipe.
    Includes validation to ensure the comment is not empty.
    """
    comment = TextAreaField(
        'Comment',
        validators=[DataRequired(), Length(min=2, max=300)],
        render_kw={
            "class": "form-control",
            "placeholder": "Enter your comment",
            "aria-describedby": "commentHelp"
        }
    )
    submit = SubmitField(
        'Add Comment',
        render_kw={
            "class": "btn btn-primary",
            "aria-label": "Submit comment"
        }
    )


# =====================================
# Bookmark Form
# =====================================
class BookmarkForm(FlaskForm):
    """
    Form to handle bookmarking recipes.
    This form only requires a submit button.
    """
    submit = SubmitField(
        'Bookmark',
        render_kw={
            "class": "btn btn-secondary",
            "aria-label": "Bookmark recipe"
        }
    )
