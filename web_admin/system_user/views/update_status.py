import logging
from django.conf import settings
from web_admin import api_settings, setup_logger
from web_admin import ajax_functions
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user


def suspend(request, system_user_id):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info('========== Start suspending system user ==========')
    url = settings.DOMAIN_NAMES + api_settings.SYSTEM_USER_STATUS_URL.format(system_user_id)
    params = {
        'is_suspended': True,
        'active_suspend_reason': request.GET.get("active_suspend_reason")
    }

    result = ajax_functions._put_method(request, url, "", logger, params)
    logger.info('========== Finish suspending system user ==========')
    return result

def activate(request, system_user_id):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info('========== Start activating system user ==========')
    url = settings.DOMAIN_NAMES + api_settings.SYSTEM_USER_STATUS_URL.format(system_user_id)
    params = {
        'is_suspended': False
    }

    result = ajax_functions._put_method(request, url, "", logger, params)
    logger.info('========== Finish activating system user ==========')
    return result