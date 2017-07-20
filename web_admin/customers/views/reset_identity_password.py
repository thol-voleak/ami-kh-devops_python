from django.conf import settings
from web_admin import api_settings
from web_admin import ajax_functions
import logging
from web_admin.utils import setup_logger
from authentications.utils import get_correlation_id_from_username

# logger = logging.getLogger(__name__)


def reset_password(request, customer_id, identity_id):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info('========== Start reset password==========')
    url = settings.DOMAIN_NAMES + api_settings.RESET_IDENTITY_PASSWORD.format(customer_id, identity_id)
    params = {}
    result = ajax_functions._post_method(request, url, "", logger, params)
    logger.info('========== Finish reset password ==========')
    return result
