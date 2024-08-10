import os
from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask import Blueprint
from flask_wtf.csrf import CSRFProtect

# Load environment variables
if os.path.exists("env.py"):
    import env

# Initialize the Flask application
app = Flask(__name__)

# Configuration settings
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")

# Initialize extensions
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
csrf = CSRFProtect(app)

# Configure LoginManager
login_manager.login_view = "login"
login_manager.login_message_category = "info"

# Custom error handling
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Register blueprints (if using blueprints for modularity)
from recipehub.routes import main, auth, recipes
app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(recipes)

# Application factory function
def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    app.config["MONGO_URI"] = os.environ.get("MONGO_URI")

    # Initialize extensions with the app
    mongo.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from recipehub.routes import main, auth, recipes
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(recipes)

    return app

if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=os.environ.get("DEBUG", "False") == "True"
    )
