from flask import Blueprint, jsonify
from flask_login import login_required, current_user

# Create a blueprint for API-related routes
api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/get_user_points', methods=['GET'])
@login_required  # Ensure that only logged-in users can access this route
def get_user_points():
    """
    Returns the current user's points as a JSON response.

    This route is protected and only accessible by authenticated users.
    """
    # Return the user's points in JSON format
    return jsonify(points=current_user.points)
