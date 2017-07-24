from django.conf import settings
from web_admin import api_settings
from web_admin import ajax_functions
import logging
from web_admin.utils import setup_logger
from authentications.utils import get_correlation_id_from_username





def activate(request, customer_id):
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
