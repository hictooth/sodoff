from flask import Blueprint, g, request
import re

from sodoff.db import get_db
from sodoff.api.common.authenticationwebservice import get_user_from_api_token
from sodoff.util.xml import generate_ds_to_string
from sodoff.api.common.des import sign_flask_response
from sodoff.schema import DisplayNameUniqueResponse, NameValidationRequest, NameValidationResponse, UserProfileData

bp = Blueprint('ProfileWebService', __name__)


@bp.route('/ProfileWebService.asmx/GetUserProfileByUserID', methods=['POST'])
@sign_flask_response
@get_user_from_api_token('apiToken')
def get_user_profile_by_user_id():
  if not g.user:
    # TODO: what response for not logged in?
    return ''

  viking_id = request.form['userId']
  db = get_db()
  viking = db.execute(
    'SELECT * FROM vikings WHERE id = ?', (viking_id,)
  ).fetchone()

  user_info = UserProfileData.UserInfo(
    UserID=None,
    ParentUserID=viking_id,
    Username=viking['name'],
    MultiplayerEnabled="true",
    GenderID=1,
    oce="true", # open chat enabled
    CreationDate=viking['created'].strftime('%Y-%m-%dT%H:%M:%S.%f')
  )
  user_subscription_info = UserProfileData.UserSubscriptionInfo(
    SubscriptionTypeID=2 # TODO: figure out what this is
  )
  user_achievement_info = UserProfileData.UserAchievementInfo(
    u=viking_id, # user id
    a='0', # points total
    r=1, # rank id
    p=1 # point type id - TODO: what is this?
  )

  avatar = UserProfileData.AvatarDisplayData(
    UserInfo=user_info,
    UserSubscriptionInfo=user_subscription_info,
    Achievements=[user_achievement_info]
  )

  response = UserProfileData.UserProfileData(
    ID=viking_id,
    Avatar=avatar,
    Ach='0', # achievement count
    Mth='0', # mythie count
    Answer=UserProfileData.UserAnswerData(ID=viking_id),
    gc='0', # game currency
    cc=75 # cash currency
  )
  res = generate_ds_to_string(response)
  a = res.replace('UserProfileData', 'UserProfileDisplayData')
  return a
