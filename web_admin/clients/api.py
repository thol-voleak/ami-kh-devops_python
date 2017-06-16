import logging
from web_admin import api_settings
from web_admin import ajax_functions
logger = logging.getLogger(__name__)


class ClientApi():
    def regenerate(request, client_id):
        logger.info('========== Start regenerating client secret ==========')
        url = api_settings.REGENERATE_CLIENT_SECRET_URL.format(client_id)
        result = ajax_functions._post_method(request, url, "regenerating client secret", logger)
        logger.info('========== Finish regenerating client secret ==========')
        return result

    def delete_client_by_id(request, client_id):
        logger.info("========== Start deleting client id ==========")
        url = api_settings.DELETE_CLIENT_URL.format(client_id)
        result = ajax_functions._delete_method(request, url, "", logger)
        logger.info('========== Finish deleting client id ==========')
        return result
