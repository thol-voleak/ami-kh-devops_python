import logging
from django.conf import settings
from web_admin import api_settings, setup_logger
from web_admin import ajax_functions
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from django.contrib import messages
import json


# logger = logging.getLogger(__name__)


def suspend(request, client_id):
    if not check_permissions_by_user(request.user, 'CAN_SUSPEND_CLIENTS'):
        return

    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info('========== Start suspending client ==========')
    url = settings.DOMAIN_NAMES + api_settings.SUSPEND_CLIENT_URL.format(client_id)
    params = {
        'status': 'suspend',
    }

    result = ajax_functions._put_method(request, url, "", logger, params)
    response = result.getvalue()
    json_data = json.loads(response.decode('utf-8'))

    if (json_data['status'] == 2):
        messages.add_message(
            request,
            messages.SUCCESS,
            message='Suspended data successfully'
        )
    logger.info('========== Finish suspending client ==========')
    return result
