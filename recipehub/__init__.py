import os
from flask import Flask, render_template, session
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin
from flask_wtf.csrf import CSRFProtect
from bson import ObjectId

# Load environment variables from env.py if it exists
if os.path.exists("env.py"):
    import env

# Global variables for extensions
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
    @login_manager.user_loader
    def load_user(user_id):
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            return User(str(user["_id"]), user["username"], user.get("profile_image", "uploads/profile_images/user-image.jpg"))
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

# Define the User model for Flask-Login
class User(UserMixin):
    def __init__(self, user_id, username, profile_image="uploads/profile_images/user-image.jpg"):
        self.id = str(user_id)  # Ensure id is a string
        self.username = username
        self.profile_image = profile_image

    @property
    def points(self):
        # Calculate and return the user's points
        recipes_count = mongo.db.recipes.count_documents({"created_by": ObjectId(self.id)})
        comments_count = mongo.db.comments.count_documents({"user_id": ObjectId(self.id)})
        points = (recipes_count * 10) + (comments_count * 2)
        mongo.db.users.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": {"points": points}}
        )
        return points

# Run the application only if this script is executed directly
if __name__ == "__main__":
    app = create_app()
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True
    )
