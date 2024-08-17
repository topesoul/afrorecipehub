import os
from flask import Flask, render_template, session
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin
from flask_wtf.csrf import CSRFProtect
from bson import ObjectId

# Load environment variables
if os.path.exists("env.py"):
    import env

mongo = None
bcrypt = None
login_manager = None

def create_app():
    app = Flask(__name__)

    # Configure the app with secret key and MongoDB URI
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    app.config["MONGO_URI"] = os.environ.get("MONGO_URI")

    # Initialize extensions
    global mongo, bcrypt, login_manager
    mongo = PyMongo(app)
    bcrypt = Bcrypt(app)
    login_manager = LoginManager(app)
    csrf = CSRFProtect(app)

    # Configure LoginManager
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # User Loader
    @login_manager.user_loader
    def load_user(user_id):
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            return User(user["_id"], user["username"])
        return None

    # Register blueprints
    from recipehub.main import bp as main_bp
    from recipehub.recipes import recipes_bp
    from recipehub.auth import auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(recipes_bp)
    app.register_blueprint(auth_bp)

    # Handle 404 and 500 errors
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500

    return app

# Define the User model for Flask-Login
class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

# Run the application
if __name__ == "__main__":
    app = create_app()
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True
    )
