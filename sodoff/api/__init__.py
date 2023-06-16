from flask import Blueprint

from .common import bp as common
from .contentserver import bp as contentserver
from .user import bp as user

bp = Blueprint('api', __name__)

bp.register_blueprint(common)
bp.register_blueprint(contentserver)
bp.register_blueprint(user)
