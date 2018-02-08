import logging
from web_admin import api_settings, setup_logger
from web_admin import ajax_functions
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from django.http import JsonResponse


def unblock(request, ticket_id):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info("Checking permission for [{}] username with [{}] permission".format(request.user, 'CAN_DELETE_FRAUD_TICKET'))
    if not check_permissions_by_user(request.user, 'CAN_DELETE_FRAUD_TICKET'):
       return JsonResponse({"status": 0, "msg": ''})
    logger.info('========== Start unblocking device ==========')
    url = api_settings.DELETE_FRAUD_TICKET.format(ticket_id=ticket_id)
    result = ajax_functions._delete_method(request, url, "", logger)
    logger.info('========== Finish unblocking device ==========')
    return result
