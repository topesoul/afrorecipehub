from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, BooleanField, PasswordField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from recipehub import mongo
from email_validator import validate_email, EmailNotValidError

class RegistrationForm(FlaskForm):
    """
    Form for user registration. Includes username, email, password, and confirmation fields.
    Validates that the username and email are unique.
    """
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        """
        Custom validator to check if the username is already taken.
        """
        user = mongo.db.users.find_one({"username": username.data})
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        """
        Custom validator to check if the email is already in use.
        """
        user = mongo.db.users.find_one({"email": email.data})
        if user:
            raise ValidationError('That email is already in use. Please choose a different one.')

class LoginForm(FlaskForm):
    """
    Form for user login. Includes fields for username and password.
    """
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ChangeUsernameForm(FlaskForm):
    """
    Form to allow users to change their username. Includes a custom validator to ensure the new username is not taken.
    """
    username = StringField('New Username', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Change Username')

    def validate_username(self, username):
        """
        Custom validator to check if the new username is already taken.
        """
        user = mongo.db.users.find_one({"username": username.data})
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

class ProfileUpdateForm(FlaskForm):
    """
    Form to allow users to update their profile, including their username and profile image.
    """
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    profile_image = FileField('Upload Profile Image')
    submit = SubmitField('Update Profile')

class RecipeForm(FlaskForm):
    """
    Form for adding or editing a recipe. Includes fields for title, description, ingredients, instructions, category, and image.
    """
    title = StringField('Recipe Title', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    ingredients = TextAreaField('Ingredients', validators=[DataRequired()])
    instructions = TextAreaField('Instructions', validators=[DataRequired()])
    category = SelectField('Category', choices=[], validators=[DataRequired()])
    image = FileField('Upload Image')
    remove_image = BooleanField('Remove Existing Image')
    submit = SubmitField('Save Recipe')

    def validate_ingredients(self, ingredients):
        """
        Custom validator to ensure that ingredients are provided in a valid format (one per line).
        """
        if not ingredients.data.strip():
            raise ValidationError('Please provide the ingredients, each on a new line.')

class CommentForm(FlaskForm):
    """
    Form for adding comments to a recipe. Includes validation to ensure the comment is not empty.
    """
    comment = TextAreaField('Comment', validators=[DataRequired(), Length(min=2, max=300)])
    submit = SubmitField('Add Comment')

class BookmarkForm(FlaskForm):
    """
    Form to handle bookmarking recipes. This form only requires a submit button.
    """
    submit = SubmitField('Bookmark')