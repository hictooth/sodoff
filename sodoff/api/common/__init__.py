from flask import Blueprint

from .des import encrypt, decrypt, KEY, CODING

from .authenticationwebservice import bp as authentication
from .registrationwebservice import bp as registration
from .membershipwebservice import bp as membership

bp = Blueprint('common', __name__)

bp.register_blueprint(authentication)
bp.register_blueprint(registration)
bp.register_blueprint(membership)
