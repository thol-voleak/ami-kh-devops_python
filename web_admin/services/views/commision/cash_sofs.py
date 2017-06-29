import logging
from web_admin.api_settings import CASH_SOFS_URL
from web_admin import ajax_functions
from web_admin.utils import setup_logger

def cash_sofs(request, user_id):
    logger = logging.getLogger(__name__)
    logger = setup_logger(request, logger)
    url = CASH_SOFS_URL
    params = {'user_id': user_id, 'user_type': 2}

    result = ajax_functions._post_method(request, url, "", logger, params)
    return result
