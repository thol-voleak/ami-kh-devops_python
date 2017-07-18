import logging
from authentications.utils import get_correlation_id_from_username
from web_admin import api_settings, setup_logger
from web_admin import ajax_functions


class ClientApi():
    def regenerate(request, client_id):
        logger = logging.getLogger(__name__)
        correlation_id = get_correlation_id_from_username(request.user)
        logger = setup_logger(request, logger, correlation_id)
        logger.info('========== Start regenerating client secret ==========')
        url = api_settings.REGENERATE_CLIENT_SECRET_URL.format(client_id)
        result = ajax_functions._post_method(request, url, "regenerating client secret", logger)
        logger.info('========== Finish regenerating client secret ==========')
        return result

    def delete_client_by_id(request, client_id):
        logger = logging.getLogger(__name__)
        correlation_id = get_correlation_id_from_username(request.user)
        logger = setup_logger(request, logger, correlation_id)
        logger.info("========== Start deleting client id ==========")
        url = api_settings.DELETE_CLIENT_URL.format(client_id)
        result = ajax_functions._delete_method(request, url, "", logger)
        logger.info('========== Finish deleting client id ==========')
        return result
