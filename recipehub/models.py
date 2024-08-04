from recipehub import mongo
from flask_login import UserMixin

class User(mongo.Document, UserMixin):
    username = mongo.StringField(max_length=60, unique=True)
    password = mongo.StringField()

class Recipe(mongo.Document):
    name = mongo.StringField(max_length=100)
    ingredients = mongo.StringField()
    instructions = mongo.StringField()
    created_by = mongo.ReferenceField(User)
