from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Length, Email, EqualTo, ValidationError
from flask_login import UserMixin

# User model class
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[InputRequired(), Length(min=4, max=25)],
        render_kw={"placeholder": "Enter Username"}
    )
    email = StringField(
        "Email",
        validators=[InputRequired(), Email()],
        render_kw={"placeholder": "Enter Email Address"}
    )
    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=8)],
        render_kw={"placeholder": "Enter Password"}
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[InputRequired(), EqualTo('password', message="Passwords must match")],
        render_kw={"placeholder": "Confirm Password"}
    )
    submit = SubmitField("Sign Up")

    # Custom validator to check if username or email already exists
    def validate_username(self, username):
        user = mongo.db.users.find_one({"username": username.data})
        if user:
            raise ValidationError("Username is already taken. Please choose a different one.")

    def validate_email(self, email):
        user = mongo.db.users.find_one({"email": email.data})
        if user:
            raise ValidationError("Email is already registered. Please choose a different one.")

class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[InputRequired(), Email()],
        render_kw={"placeholder": "Enter Email Address"}
    )
    password = PasswordField(
        "Password",
        validators=[InputRequired()],
        render_kw={"placeholder": "Enter Password"}
    )
    submit = SubmitField("Log In")

class RecipeForm(FlaskForm):
    title = StringField(
        "Recipe Title",
        validators=[InputRequired(), Length(min=2, max=100)],
        render_kw={"placeholder": "Enter Recipe Title"}
    )
    ingredients = TextAreaField(
        "Ingredients",
        validators=[InputRequired()],
        render_kw={"placeholder": "List the ingredients"}
    )
    instructions = TextAreaField(
        "Instructions",
        validators=[InputRequired()],
        render_kw={"placeholder": "Provide the cooking instructions"}
    )
    category = SelectField(
        "Category",
        coerce=str,  # To match MongoDB ObjectId stored as string
    )
    submit = SubmitField("Save Recipe")

class CommentForm(FlaskForm):
    comment = TextAreaField(
        "Comment",
        validators=[InputRequired(), Length(min=1, max=500)],
        render_kw={"placeholder": "Add your comment"}
    )
    submit = SubmitField("Submit Comment")
