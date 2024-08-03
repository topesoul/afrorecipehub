from flask_login import UserMixin
from app import login_manager

@login_manager.user_loader
def load_user(user_id):
    user = mongo.db.users.find_one({"_id": user_id})
    if user:
        return User(user)
    return None

class User(UserMixin):
    def __init__(self, user):
        self.id = user['_id']
        self.username = user['username']
        self.password = user['password']
