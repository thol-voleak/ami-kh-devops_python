from django.conf import settings
from web_admin import api_settings, setup_logger
from web_admin import ajax_functions
import logging
from web_admin.api_settings import DELETE_CATEGORY
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user


def delete(request, categoryId):

    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)

    logger.info('========== Start deleting category ==========')
    url = settings.DOMAIN_NAMES + DELETE_CATEGORY.format(category_id=categoryId)

    result = ajax_functions._delete_method(request, url, "", logger)
    logger.info('========== Finish deleting category ==========')
    return result