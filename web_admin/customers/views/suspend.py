import logging
from django.conf import settings
from web_admin import api_settings
from web_admin import ajax_functions
from web_admin.utils import setup_logger


# logger = logging.getLogger(__name__)


def suspend(request, customer_id):
    logger = logging.getLogger(__name__)
    logger = setup_logger(request, logger)
    logger.info('========== Start suspending customer ==========')
    print("customer id is : {}>>>>>>>>>>>".format(customer_id))
    url = settings.DOMAIN_NAMES + api_settings.SUSPEND_CUSTOMER.format(customer_id)
    params = {
        'is_suspended': 'true',
    }
    result = ajax_functions._put_method(request, url, "", logger, params)
    logger.info('========== Finish suspending customer ==========')
    return result