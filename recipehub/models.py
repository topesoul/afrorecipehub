from flask_login import UserMixin
from recipehub import mongo
from bson.objectid import ObjectId

class User(UserMixin):
    def __init__(self, user_id, username, profile_image=None, points=0):
        self.id = user_id
        self.username = username
        self.profile_image = profile_image
        self._points = points

    @property
    def points(self):
        # Retrieve the most current points from the database
        user = mongo.db.users.find_one({"_id": ObjectId(self.id)})
        if user:
            return user.get("points", 0)
        return 0

    @staticmethod
    def get_user_by_id(user_id):
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            return User(
                str(user["_id"]),
                user["username"],
                user.get("profile_image"),
                user.get("points", 0)
            )

    @staticmethod
    def get_user_by_username(username):
        user = mongo.db.users.find_one({"username": username})
        if user:
            return User(
                str(user["_id"]),
                user["username"],
                user.get("profile_image"),
                user.get("points", 0)
            )