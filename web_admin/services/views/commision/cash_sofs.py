import logging
from web_admin.api_settings import CASH_SOFS_URL
from web_admin import ajax_functions
from authentications.utils import get_correlation_id_from_username
from web_admin import setup_logger

def cash_sofs(request, user_id):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    url = CASH_SOFS_URL
    params = {'user_id': user_id, 'user_type': 2}

    result = ajax_functions._post_method(request, url, "", logger, params)
    return result
