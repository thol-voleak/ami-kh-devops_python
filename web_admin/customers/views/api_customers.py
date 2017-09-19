from web_admin import api_settings
from web_admin import ajax_functions
from web_admin.utils import setup_logger
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user

from django.conf import settings

import logging


def activate(request, customer_id):
    if not check_permissions_by_user(request.user, 'CAN_SUSPEND_CUSTOMER'):
        return

    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info('========== Start activating customer ==========')
    url = settings.DOMAIN_NAMES + api_settings.ACTIVATE_CUSTOMER.format(customer_id)
    params = {
        'is_suspended': 'false',
    }

    result = ajax_functions._put_method(request, url, "", logger, params)
    logger.info('========== Finish activating customer ==========')
    return result


def delete_customer(request, customer_id):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info('========== Start delete customer ==========')

    if request.method == 'POST':
        logger.info('Sending request to backend service')
        url = settings.DOMAIN_NAMES + api_settings.ADMIN_DELETE_CUSTOMER_URL.format(customer_id)

        result = ajax_functions._delete_method(request=request,
                                               api_path=url,
                                               func_description="",
                                               logger=logger)
        logger.info('========== Finish activating customer ==========')
        return result
