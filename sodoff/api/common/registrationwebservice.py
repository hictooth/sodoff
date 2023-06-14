from flask import Blueprint, request
from werkzeug.security import generate_password_hash
from uuid import uuid4
from html import escape

from sodoff.util.xml import generate_ds_to_string
from sodoff.api.common.des import encrypt_flask_response, decrypt_flask_request, sign_flask_response, ENCODING_WRAPPING_XML_STRING
from sodoff.schema import ParentRegistrationData, RegistrationResult, ParentLoginInfo
from sodoff.db import get_db

bp = Blueprint('RegistrationWebService', __name__)


@bp.route('/v3/RegistrationWebService.asmx/RegisterParent', methods=['POST'])
@sign_flask_response
@decrypt_flask_request('parentRegistrationData')
@encrypt_flask_response(ENCODING_WRAPPING_XML_STRING)
def register_parent():
  parentRegistrationDataSerialised = request.form['parentRegistrationData']
  print(parentRegistrationDataSerialised)
  parentRegistrationData = ParentRegistrationData.parseString(parentRegistrationDataSerialised.encode('utf-16'))

  # first parse out the parent data
  email = parentRegistrationData.get_Email().strip()
  password = parentRegistrationData.get_Password().strip()
  # locale, birth date, receives_email, subscription_id, child_list, from_api_key, to_api_key, api_token,
  # has_aquisition_source, face_book_user_id, facebook_access_token, favourite_team_id, group_id, send_activation_email,
  # auto_activate, send_welcome_email, is_anonymous, required_login, link_user_to_facebook, client_ip, external_auth_provider
  # external_user_id, external_auth_data, user_policy, email_notification

  # now parse out the child data
  child = parentRegistrationData.get_ChildList()[0]
  username = child.get_ChildName()

  if not (email and username and password):
    response = RegistrationResult.RegistrationResult(
      Status=RegistrationResult.MembershipUserStatus.VALIDATION_ERROR,
    )
    return generate_ds_to_string(response)
  
  try:
    db = get_db()
    id = str(uuid4())
    db.execute(
      "INSERT INTO users (id, email, username, password) VALUES (?, ?, ?, ?)",
      (id, email, username, generate_password_hash(password)),
    )
    db.commit()
  except db.IntegrityError:
    print('integrity!')
    response = RegistrationResult.RegistrationResult(
      Status=RegistrationResult.MembershipUserStatus.DUPLICATE_USER_NAME, # TODO: for now, do duplicate username even if its email
    )
    return generate_ds_to_string(response)
  
  parentLoginInfo = ParentLoginInfo.ParentLoginInfo(
    UserName=username,
    ApiToken=str(uuid4()), # TODO: I don't think we use this anywhere, but check,
    UserID=id,
    LoginStatus=ParentLoginInfo.MembershipUserStatus.SUCCESS,
    UnAuthorized="false" # TODO: I think we can set this to true right away, but check
  )
  parentLoginInfo = generate_ds_to_string(parentLoginInfo)
  parentLoginInfo = escape(parentLoginInfo)

  response = RegistrationResult.RegistrationResult(
    ParentLoginInfo=parentLoginInfo,
    UserID=id,
    Status=RegistrationResult.MembershipUserStatus.SUCCESS,
    ApiToken=str(uuid4()) # TODO: I don't think we use this anywhere, but check
  )
  return generate_ds_to_string(response)
