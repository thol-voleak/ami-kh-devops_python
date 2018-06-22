from web_admin import setup_logger, api_settings
from web_admin import ajax_functions
from authentications.utils import get_correlation_id_from_username
import logging


def get_user_name(request):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info('========== Start get user name ==========')
    user_id = request.POST.get('id')
    user_type = request.POST.get('type')
    if user_type == "2":
        url = api_settings.SEARCH_AGENT
    else:
        url = api_settings.MEMBER_CUSTOMER_PATH
    params = {
        'id': user_id
    }
    result = ajax_functions._post_method(request, url, "", logger, params)
    logger.info('========== Finish get user name ==========')
    return result
