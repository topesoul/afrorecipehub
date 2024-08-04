from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=20)])
    submit = SubmitField('Login')

class RecipeForm(FlaskForm):
    name = StringField('Recipe Name', validators=[InputRequired(), Length(min=1, max=100)])
    ingredients = TextAreaField('Ingredients', validators=[InputRequired()])
    instructions = TextAreaField('Instructions', validators=[InputRequired()])
    submit = SubmitField('Submit')
