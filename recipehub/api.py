from flask import Blueprint, jsonify
from flask_login import login_required, current_user

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/get_user_points', methods=['GET'])
@login_required
def get_user_points():
    return jsonify(points=current_user.points)
