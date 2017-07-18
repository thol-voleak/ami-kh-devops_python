from django.conf import settings
from web_admin import api_settings, setup_logger
from web_admin import ajax_functions
import logging
from authentications.utils import get_correlation_id_from_username


# logger = logging.getLogger(__name__)


def activate(request, client_id):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info('========== Start activating client ==========')
    url = settings.DOMAIN_NAMES + api_settings.ACTIVATE_CLIENT_URL.format(client_id)
    params = {
        'status': 'active',
    }
    result = ajax_functions._put_method(request, url, "", logger, params)
    logger.info('========== Finish activating client ==========')
    return result

