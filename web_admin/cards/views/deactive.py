from django.conf import settings
from web_admin import api_settings, setup_logger
from web_admin import ajax_functions
import logging
from web_admin.api_settings import ACTIVATE_CARD_PATH
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user


def deactive(request, id):

    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)

    logger.info('========== Start deactivating card ==========')
    url = settings.DOMAIN_NAMES + ACTIVATE_CARD_PATH.format(card_id=id)
    params = {
        'is_stopped': True
    }
    result = ajax_functions._put_method(request, url, "", logger, params)
    logger.info('========== Finish deactivating card ==========')
    return result
