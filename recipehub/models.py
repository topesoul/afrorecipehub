from flask_login import UserMixin
from recipehub import mongo
from bson.objectid import ObjectId

class User(UserMixin):
    def __init__(self, user_id, username, profile_image=None):
        self.id = user_id
        self.username = username
        self.profile_image = profile_image

    @staticmethod
    def get_user_by_id(user_id):
        return mongo.db.users.find_one({"_id": ObjectId(user_id)})

    @staticmethod
    def get_user_by_username(username):
        return mongo.db.users.find_one({"username": username})
