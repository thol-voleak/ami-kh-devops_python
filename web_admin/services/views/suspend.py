import logging
from django.conf import settings
from web_admin import api_settings, setup_logger
from web_admin import ajax_functions
from authentications.utils import get_correlation_id_from_username


def suspend(request, service_id):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info('========== Start suspending service ==========')
    url = settings.DOMAIN_NAMES + api_settings.SERVICE_URL.format(service_id)
    params = {
        'status': 0,
        'is_update_status': 1
    }

    result = ajax_functions._put_method(request, url, "", logger, params)
    logger.info('========== Finish suspending service ==========')
    return result
