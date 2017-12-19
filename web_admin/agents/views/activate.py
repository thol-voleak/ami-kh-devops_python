from django.conf import settings
from web_admin import api_settings, setup_logger
from web_admin import ajax_functions
import logging
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user


def activate(request, agent_id):
    # if not check_permissions_by_user(request.user, 'CAN_SUSPEND_AGENTS'):
    #     return

    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info('========== Start activating agent ==========')
    url = settings.DOMAIN_NAMES + api_settings.AGENT_STATUS_URL.format(agent_id)
    params = {
        'is_suspended': False,
    }
    result = ajax_functions._put_method(request, url, "", logger, params)
    logger.info('========== Finish activating agent ==========')
    return result
