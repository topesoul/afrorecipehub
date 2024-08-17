from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, BooleanField, PasswordField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from recipehub import mongo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = mongo.db.users.find_one({"username": username.data})
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = mongo.db.users.find_one({"email": email.data})
        if user:
            raise ValidationError('That email is already in use. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ChangeUsernameForm(FlaskForm):
    username = StringField('New Username', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Change Username')

    def validate_username(self, username):
        user = mongo.db.users.find_one({"username": username.data})
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

class ProfileUpdateForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    profile_image = FileField('Upload Profile Image')
    submit = SubmitField('Update Profile')

class RecipeForm(FlaskForm):
    title = StringField('Recipe Title', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    ingredients = TextAreaField('Ingredients', validators=[DataRequired()])
    instructions = TextAreaField('Instructions', validators=[DataRequired()])
    category = SelectField('Category', choices=[], validators=[DataRequired()])
    image = FileField('Upload Image')
    submit = SubmitField('Add Recipe')

class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', validators=[DataRequired(), Length(min=2, max=300)])
    submit = SubmitField('Add Comment')