from flask import Blueprint

from .profilewebservice import bp as profile

bp = Blueprint('user', __name__)

bp.register_blueprint(profile)
