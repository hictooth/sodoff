from flask import Blueprint

from .contentwebservice import bp as content

bp = Blueprint('contentserver', __name__)

bp.register_blueprint(content)
