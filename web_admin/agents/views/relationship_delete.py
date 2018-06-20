import logging
from django.conf import settings
from web_admin import api_settings, setup_logger
from web_admin import ajax_functions
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user


def delete_relationship(request, relationship_id):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info("Checking permission for [{}] username with [{}] permission".format(request.user, 'CAN_DELETE_RELATIONSHIP'))
    if not check_permissions_by_user(request.user, 'CAN_DELETE_RELATIONSHIP'):
        return {"status": 1, "msg": ''}
    logger.info('========== Start delete relationship ==========')
    url = settings.DOMAIN_NAMES + api_settings.DELETE_RELATIONSHIP.format(relationship_id)

    result = ajax_functions._delete_method(request, url, "", logger)
    logger.info('========== Finish delete relationship ==========')
    return result
