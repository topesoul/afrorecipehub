from flask_pymongo import PyMongo

# Create a PyMongo instance
mongo = PyMongo()

def init_app(app):
    """
    Initialize the Flask application with PyMongo.
    
    :param app: The Flask application instance
    """
    # Initialize the PyMongo instance with the Flask app
    mongo.init_app(app)
