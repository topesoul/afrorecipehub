from flask import Flask
from flask_pymongo import PyMongo
from flask_login import UserMixin, LoginManager
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError

app = Flask(__name__)
app.config["MONGO_URI"] = "your_mongo_db_uri"
mongo = PyMongo(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return mongo.db.users.find_one({"_id": user_id})

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data["_id"]
        self.username = user_data["username"]
        self.password = user_data["password"]

class Recipe:
    def __init__(self, recipe_data):
        self.id = recipe_data["_id"]
        self.title = recipe_data["title"]
        self.ingredients = recipe_data["ingredients"]
        self.instructions = recipe_data["instructions"]
        self.category = recipe_data["category"]

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
