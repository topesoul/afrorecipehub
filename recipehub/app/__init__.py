import os
from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

if os.path.exists("env.py"):
    import env

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

from app.auth import auth as auth_blueprint
from app.recipes import recipes as recipes_blueprint
from app.routes import main as main_blueprint

app.register_blueprint(auth_blueprint)
app.register_blueprint(recipes_blueprint)
app.register_blueprint(main_blueprint)
