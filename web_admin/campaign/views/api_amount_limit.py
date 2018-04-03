from web_admin import api_settings
from web_admin import ajax_functions
from web_admin.utils import setup_logger
from authentications.utils import get_correlation_id_from_username

from django.conf import settings

import logging



def delete_amount_limit(request, rule_id, rule_limit_id):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info('========== Start delete campaign amount limit ==========')

    if request.method == 'POST':
        url = settings.DOMAIN_NAMES + api_settings.DELETE_RULE_AMOUNT_LIMIT.format(rule_id=rule_id, rule_limit_id=rule_limit_id)
        result = ajax_functions._delete_method(request=request,
                                               api_path=url,
                                               func_description="",
                                               logger=logger)
        logger.info('========== Finish delete campaign amount limit ==========')
        return result
