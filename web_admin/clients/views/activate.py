from django.conf import settings
from web_admin import api_settings
from web_admin import ajax_functions
import logging

logger = logging.getLogger(__name__)


def activate(request, client_id):
    logger.info('========== Start activating client ==========')
    url = settings.DOMAIN_NAMES + api_settings.ACTIVATE_CLIENT_URL.format(client_id)
    params = {
        'status': 'active',
    }
    result = ajax_functions._put_method(request, url, "", logger, params)
    logger.info('========== Finish activating client ==========')
    return result

