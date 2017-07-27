import logging
from django.conf import settings
from web_admin import api_settings
from web_admin import ajax_functions
from web_admin.utils import setup_logger
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from django.contrib import messages
import json

def suspend(request, customer_id):
    if not check_permissions_by_user(request.user, 'CAN_SUSPEND_CUSTOMER'):
        return

    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info('========== Start suspending customer ==========')
    url = settings.DOMAIN_NAMES + api_settings.SUSPEND_CUSTOMER.format(customer_id)
    params = {
        'is_suspended': 'true',
    }
    result = ajax_functions._put_method(request, url, "", logger, params)
    response = result.getvalue()
    json_data = json.loads(response)

    if (json_data['status'] == 2):
        messages.add_message(
            request,
            messages.SUCCESS,
            message='Suspended data successfully'
        )


    logger.info('========== Finish suspending customer ==========')
    return result