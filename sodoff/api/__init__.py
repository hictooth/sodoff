from flask import Blueprint

from .common import bp as common

bp = Blueprint('api', __name__)

bp.register_blueprint(common)