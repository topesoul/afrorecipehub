from flask import Blueprint, render_template, request

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html')

@bp.route('/about')
def about():
    return render_template('about.html')
