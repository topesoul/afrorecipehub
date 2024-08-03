from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from app import mongo

class RegisterForm(FlaskForm):
    username = StringField(
        validators=[
            InputRequired(),
            Length(min=4, max=20)
        ],
        render_kw={"placeholder": "Username"}
    )
    email = StringField(
        validators=[
            InputRequired(),
        ],
        render_kw={"placeholder": "Email"}
    )
    password = PasswordField(
        validators=[
            InputRequired(),
            Length(min=8, max=20)
        ],
        render_kw={"placeholder": "Password"}
    )
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = mongo.db.users.find_one({"username": username.data})
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField(
        validators=[
            InputRequired(),
        ],
        render_kw={"placeholder": "Email"}
    )
    password = PasswordField(
        validators=[
            InputRequired(),
            Length(min=8, max=20)
        ],
        render_kw={"placeholder": "Password"}
    )
    submit = SubmitField('Login')
