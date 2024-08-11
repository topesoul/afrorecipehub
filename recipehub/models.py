from flask_login import UserMixin
from recipehub import mongo
from bson.objectid import ObjectId

class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = str(user_id)
        self.username = username

    @staticmethod
    def get_user_by_id(user_id):
        print(f"Fetching user by ID {user_id}")
        return mongo.db.users.find_one({"_id": ObjectId(user_id)})

    @staticmethod
    def get_user_by_username(username):
        print(f"Fetching user by username {username}")
        return mongo.db.users.find_one({"username": username})
