import logging
from django.conf import settings
from web_admin import api_settings
from web_admin import ajax_functions
logger = logging.getLogger(__name__)


def suspend(request, client_id):
    logger.info('========== Start suspending client ==========')
    url = settings.DOMAIN_NAMES + api_settings.SUSPEND_CLIENT_URL.format(client_id)
    params = {
        'status': 'suspend',
    }
    result = ajax_functions._put_method(request, url, "", logger, params)
    logger.info('========== Finish suspending client ==========')
    return result
