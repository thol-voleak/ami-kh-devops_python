from django.conf import settings
from web_admin import api_settings
from web_admin import ajax_functions
import logging
from web_admin.utils import setup_logger


# logger = logging.getLogger(__name__)


def reset_password(request, customer_id, identity_id):
    logger = logging.getLogger(__name__)
    logger = setup_logger(request, logger)
    logger.info('========== Start reset password==========')
    url = settings.DOMAIN_NAMES + api_settings.RESET_IDENTITY_PASSWORD.format(customer_id, identity_id)
    params = {}
    result = ajax_functions._post_method(request, url, "", logger, params, timeout=settings.RESET_PASSWORD_TIMEOUT)
    logger.info('========== Finish reset password ==========')
    return result
