from flask import Blueprint

from sodoff.util.xml import generate_ds_to_string
from sodoff.api.common.des import sign_flask_response
from sodoff.schema import SubscriptionInfo

bp = Blueprint('MembershipWebService', __name__)


@bp.route('/MembershipWebService.asmx/GetSubscriptionInfo', methods=['POST'])
@sign_flask_response
def get_subscription_info():
  response = SubscriptionInfo.SubscriptionInfo(Recurring=True, Status="Member", SubscriptionTypeID=1, SubscriptionEndDate="2033-06-13T16:17:18")
  return generate_ds_to_string(response)