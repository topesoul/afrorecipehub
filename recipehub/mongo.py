from flask_pymongo import PyMongo

# Initialize PyMongo
mongo = PyMongo()

def init_app(app):
    # Configure the database
    app.config["MONGO_URI"] = app.config["MONGO_URI"]
    mongo.init_app(app)

# User-related operations
def get_user_by_id(user_id):
    return mongo.db.users.find_one({"_id": user_id})

def get_user_by_username(username):
    return mongo.db.users.find_one({"username": username})

def insert_user(user):
    return mongo.db.users.insert_one(user)

def update_user(user_id, updates):
    return mongo.db.users.update_one({"_id": user_id}, {"$set": updates})

# Recipe-related operations
def get_recipe_by_id(recipe_id):
    return mongo.db.recipes.find_one({"_id": recipe_id})

def get_recipes_by_user(user_id):
    return mongo.db.recipes.find({"created_by": user_id})

def insert_recipe(recipe):
    return mongo.db.recipes.insert_one(recipe)

def update_recipe(recipe_id, updates):
    return mongo.db.recipes.update_one({"_id": recipe_id}, {"$set": updates})

def delete_recipe(recipe_id):
    return mongo.db.recipes.delete_one({"_id": recipe_id})

# Comment-related operations
def get_comments_by_recipe(recipe_id):
    return mongo.db.comments.find({"recipe_id": recipe_id})

def insert_comment(comment):
    return mongo.db.comments.insert_one(comment)
