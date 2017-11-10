import logging
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import api_settings, setup_logger
from web_admin import ajax_functions


class CampaignApi():
    def delete_mechanic_by_id(request, campaign_id, mechanic_id):
        if not check_permissions_by_user(request.user, 'CAN_DELETE_MECHANIC'):
            return
        logger = logging.getLogger(__name__)
        correlation_id = get_correlation_id_from_username(request.user)
        logger = setup_logger(request, logger, correlation_id)
        logger.info("========== Start deleting mechanic ==========")
        url = api_settings.DELETE_MECHANIC_URL.format(campaign_id=campaign_id, mechanic_id=mechanic_id)
        result = ajax_functions._delete_method(request, url, "", logger)
        logger.info('========== Finish deleting mechanic ==========')
        return result