from flask import Blueprint, request, g
from werkzeug.security import check_password_hash
from uuid import uuid4
from functools import wraps

from sodoff.db import get_db
from sodoff.util.xml import generate_ds_to_string
from sodoff.api.common.des import encrypt_flask_response, decrypt_flask_request, sign_flask_response, ENCODING_WRAPPING_XML_STRING
from sodoff.schema import GetProductRulesResponse, ParentLoginData, ParentLoginInfo, UserInfo, MembershipUserStatus, Gender

bp = Blueprint('AuthenticationWebService', __name__)


def get_user_from_api_token(token_name):
  def decorator(view):
    @wraps(view)
    def wrapped_view(**kwargs):
      # get the token
      api_token = request.form[token_name]

      # get the session
      db = get_db()
      session = db.execute(
        'SELECT * FROM sessions WHERE api_token = ?', (api_token,)
      ).fetchone()

      # retrieve user
      g.user = None
      g.viking = None
      if session is not None:

        if session['type'] == 1: # a user
          g.user = db.execute(
            'SELECT * FROM users WHERE id = ?', (session['user_id'],)
          ).fetchone()
        
        elif session['type'] == 2: # a viking
          g.viking = db.execute(
            'SELECT * FROM vikings WHERE id = ?', (session['user_id'],)
          ).fetchone()
      
      # render as normal
      return view(**kwargs)
    return wrapped_view
  return decorator


@bp.route('/v3/AuthenticationWebService.asmx/GetRules', methods=['POST'])
@sign_flask_response
@encrypt_flask_response(ENCODING_WRAPPING_XML_STRING)
def get_rules():
  response = GetProductRulesResponse.getProductRulesResponse(
    globalKey="11A0CC5A-C4DF-4A0E-931C-09A44C9966AE"
  )
  return generate_ds_to_string(response)


@bp.route('/v3/AuthenticationWebService.asmx/LoginParent', methods=['POST'])
@sign_flask_response
@decrypt_flask_request('parentLoginData')
@encrypt_flask_response(ENCODING_WRAPPING_XML_STRING)
def login_parent():
  parentLoginDataSerialised = request.form['parentLoginData']
  parentLoginData = ParentLoginData.parseString(parentLoginDataSerialised.encode('utf-16'))

  username = parentLoginData.get_UserName().strip()
  password = parentLoginData.get_Password().strip()

  if not (username and password):
    # return INVALID_PASSWORD as that gives a generic error message
    response = ParentLoginInfo.ParentLoginInfo(
      LoginStatus=MembershipUserStatus.MembershipUserStatus.INVALID_PASSWORD,
    )
    return generate_ds_to_string(response)
  
  db = get_db()
  user = db.execute(
    'SELECT * FROM users WHERE username = ?', (username,)
  ).fetchone()

  if user is None:
    response = ParentLoginInfo.ParentLoginInfo(
      LoginStatus=MembershipUserStatus.MembershipUserStatus.INVALID_USER_NAME,
    )
    return generate_ds_to_string(response)
  
  if not check_password_hash(user['password'], password):
    response = ParentLoginInfo.ParentLoginInfo(
      LoginStatus=MembershipUserStatus.MembershipUserStatus.INVALID_PASSWORD,
    )
    return generate_ds_to_string(response)
  
  # on success, setup session
  api_token = str(uuid4())
  db.execute(
    "INSERT INTO sessions (api_token, user_id, type) VALUES (?, ?, 1)",
    (api_token, user['id']),
  )
  db.commit()
  
  # return logged in info
  response = ParentLoginInfo.ParentLoginInfo(
    UserName=user['username'],
    Email=user['email'],
    ApiToken=api_token,
    UserID=user['id'],
    LoginStatus=MembershipUserStatus.MembershipUserStatus.SUCCESS,
    SendActivationReminder="false",
    UnAuthorized="false"
  )
  return generate_ds_to_string(response)


@bp.route('/AuthenticationWebService.asmx/GetUserInfoByApiToken', methods=['POST'])
@sign_flask_response
@get_user_from_api_token('apiToken')
def get_user_info_by_api_token():
  if g.user:
    response = UserInfo.UserInfo(
      UserID=g.user['id'],
      Username=g.user['username'],
      MultiplayerEnabled="true",
      Age=24,
      oce="true",
    )
  elif g.viking:
    response = UserInfo.UserInfo(
      UserID=g.viking['id'],
      Username=g.viking['name'],
      MultiplayerEnabled="true",
      Age=24,
      oce="true",
    )
  else:
    # TODO: error response
    return ''
  res = generate_ds_to_string(response, add_xmlns=True)
  return res


@bp.route('/AuthenticationWebService.asmx/RecoverAccount', methods=['POST'])
@sign_flask_response
def recover_account():
  email = request.form['email']
  # TODO: implement this
  # TODO: bug in generateDS breakes this xml, so just return string for not
  return '<?xml version="1.0" encoding="utf-8"?><MembershipUserStatus>Success</MembershipUserStatus>'


@bp.route('/v3/AuthenticationWebService.asmx/ResetPassword', methods=['POST'])
@sign_flask_response
def reset_password():
  email = request.form['email']
  username = request.form['username']
  # TODO: implement this
  # TODO: bug in generateDS breakes this xml, so just return string for not
  return '<?xml version="1.0" encoding="utf-8"?><MembershipUserStatus>Success</MembershipUserStatus>'


@bp.route('/AuthenticationWebService.asmx/IsValidApiToken_V2', methods=['POST'])
@sign_flask_response
@get_user_from_api_token('apiToken')
def is_valid_api_token():
  if g.user is None and g.viking is None:
    return '<?xml version="1.0" encoding="utf-8"?><ApiTokenStatus>3</ApiTokenStatus>'
  return '<?xml version="1.0" encoding="utf-8"?><ApiTokenStatus>1</ApiTokenStatus>'


@bp.route('/AuthenticationWebService.asmx/LoginChild', methods=['POST'])
@sign_flask_response
@decrypt_flask_request('childUserID')
@encrypt_flask_response(ENCODING_WRAPPING_XML_STRING)
@get_user_from_api_token('parentApiToken')
def login_child():
  if g.user is None:
    # TODO: response for bad
    return ''

  childUserIDSerialised = request.form['childUserID']

  # on success, setup session
  api_token = str(uuid4())
  db = get_db()
  db.execute(
    "INSERT INTO sessions (api_token, user_id, type) VALUES (?, ?, 2)",
    (api_token, childUserIDSerialised),
  )
  db.commit()

  return api_token