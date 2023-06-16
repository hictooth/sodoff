from flask import Blueprint, g, request
import re

from sodoff.db import get_db
from sodoff.api.common.authenticationwebservice import get_user_from_api_token
from sodoff.util.xml import generate_ds_to_string
from sodoff.api.common.des import sign_flask_response
from sodoff.schema import DisplayNameUniqueResponse, NameValidationRequest, NameValidationResponse

bp = Blueprint('ContentWebService', __name__)


@bp.route('/ContentWebService.asmx/GetDefaultNameSuggestion', methods=['POST'])
@sign_flask_response
def get_default_name_suggestion():
  # TODO: generate random names, and ensure they aren't already taken
  response = DisplayNameUniqueResponse.DisplayNameUniqueResponse(
    suggestions=DisplayNameUniqueResponse.SuggestionResult(Suggestion=["dragon1", "dragon2", "dragon3"])
  )
  return generate_ds_to_string(response)


@bp.route('/V2/ContentWebService.asmx/ValidateName', methods=['POST'])
@sign_flask_response
@get_user_from_api_token('apiToken')
def validate_name():
  if g.user is None:
    # if user is not logged in, always respond with already taken
    # there's probably a better response but this will do for now
    response = NameValidationResponse.NameValidationResponse(Category='3')
    return generate_ds_to_string(response)
  
  nameValidationRequestSerialised = request.form['nameValidationRequest'].replace('\n', '').replace('\r', '').encode('utf-8')
  nameValidationRequest = NameValidationRequest.parseString(nameValidationRequestSerialised)
  name = nameValidationRequest.get_Name()
  category = nameValidationRequest.get_Category()

  if category == 4:
    # this is a avatar we are checking
    db = get_db()
    avatar = db.execute(
      'SELECT * FROM vikings WHERE name = ?', (name,)
    ).fetchone()

    if avatar is None:
      # 1 meaning ok
      response = NameValidationResponse.NameValidationResponse(Category='1')
    else:
      # 3 meaning already taken
      response = NameValidationResponse.NameValidationResponse(Category='3')
    return generate_ds_to_string(response)

  else:
    # TODO: pets, groups, default??
    return ''
