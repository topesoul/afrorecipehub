import os
import logging
from flask_login import UserMixin
from recipehub import mongo
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class User(UserMixin):
    def __init__(self, user_id, username, profile_image=None, points=None):
        """
        Initialize a User object.

        :param user_id: User's ID.
        :param username: User's username.
        :param profile_image: URL or path to the user's profile image.
        :param points: User's points, if already calculated.
        """
        self.id = user_id
        self.username = username
        self.profile_image = profile_image if profile_image else "uploads/profile_images/user-image.jpg"
        self._points = points  # Points are set if provided, otherwise, they are lazy-loaded

    @property
    def points(self):
        """
        Property to access user's points. Recalculates if necessary.
        
        :return: User's points.
        """
        if self._points is None:
            self._points = self.calculate_points()
        return self._points

    def calculate_points(self):
        """
        Calculate the user's points based on the number of recipes and comments they have created.

        :return: Calculated points.
        """
        try:
            recipes_count = mongo.db.recipes.count_documents({"created_by": ObjectId(self.id)})
            comments_count = mongo.db.comments.count_documents({"user_id": ObjectId(self.id)})
            points = (recipes_count * 10) + (comments_count * 2)

            # Update the points in the database
            mongo.db.users.update_one(
                {"_id": ObjectId(self.id)},
                {"$set": {"points": points}}
            )

            self._points = points  # Cache the calculated points
            return points
        except PyMongoError as e:
            logger.error(f"An error occurred while calculating points for user {self.id}: {e}")
            return 0  # Return 0 points if an error occurs

    @staticmethod
    def calculate_points_static(user_id):
        """
        Calculate the user's points based on the number of recipes and comments they have created.
        This method is static and does not require an instance of the User class.

        :param user_id: The user's ID.
        :return: Calculated points.
        """
        try:
            recipes_count = mongo.db.recipes.count_documents({"created_by": ObjectId(user_id)})
            comments_count = mongo.db.comments.count_documents({"user_id": ObjectId(user_id)})
            points = (recipes_count * 10) + (comments_count * 2)

            # Update the points in the database
            mongo.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"points": points}}
            )

            return points
        except PyMongoError as e:
            logger.error(f"An error occurred while calculating points for user {user_id}: {e}")
            return 0  # Return 0 points if an error occurs

    @staticmethod
    def get_user_by_id(user_id):
        """
        Retrieve a User object by their ID.

        :param user_id: User's ID.
        :return: User object or None if user not found or error occurs.
        """
        try:
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                return User(
                    str(user["_id"]),
                    user["username"],
                    user.get("profile_image"),
                    user.get("points")  # Avoid recalculating if already stored
                )
            return None
        except PyMongoError as e:
            logger.error(f"An error occurred while retrieving user by ID {user_id}: {e}")
            return None

    @staticmethod
    def get_user_by_username(username):
        """
        Retrieve a User object by their username.

        :param username: User's username.
        :return: User object or None if user not found or error occurs.
        """
        try:
            user = mongo.db.users.find_one({"username": username})
            if user:
                return User(
                    str(user["_id"]),
                    user["username"],
                    user.get("profile_image"),
                    user.get("points")  # Avoid recalculating if already stored
                )
            return None
        except PyMongoError as e:
            logger.error(f"An error occurred while retrieving user by username {username}: {e}")
            return None
