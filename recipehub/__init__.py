import os
from flask import Flask, render_template, session
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from bson import ObjectId

# Load environment variables from env.py if it exists
if os.path.exists("env.py"):
    import env

# Initialize the Flask app and extensions
mongo = None
bcrypt = None
login_manager = None

def create_app():
    app = Flask(
        __name__,
        static_folder='static',  # Specify the folder for static files
        static_url_path='/static'  # Specify the URL path for serving static files
    )

    # Configure the app with secret key and MongoDB URI from environment variables
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    app.config["MONGO_URI"] = os.environ.get("MONGO_URI")

    # Initialize extensions with the Flask app
    global mongo, bcrypt, login_manager
    mongo = PyMongo(app)
    bcrypt = Bcrypt(app)
    login_manager = LoginManager(app)
    csrf = CSRFProtect(app)

    # Configure LoginManager
    login_manager.login_view = "auth.login"  # Redirects to login page if user is not logged in
    login_manager.login_message_category = "info"  # Flash message category for login

    # User Loader for Flask-Login
    from recipehub.models import User  # Import the User class from models

    @login_manager.user_loader
    def load_user(user_id):
        user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(
                user_id=str(user_data["_id"]),
                username=user_data["username"],
                profile_image=user_data.get("profile_image", "uploads/profile_images/user-image.jpg"),
                points=user_data.get("points")
            )
        return None

    # Register blueprints for modularizing the application
    from recipehub.main import bp as main_bp
    from recipehub.recipes import recipes_bp
    from recipehub.auth import auth_bp
    from recipehub.api import api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(recipes_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    # Error handlers for 404 and 500 errors
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500

    return app

# Run the application only if this script is executed directly
if __name__ == "__main__":
    app = create_app()
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True
    )
