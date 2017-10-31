from django.conf import settings
from web_admin import api_settings, setup_logger
from web_admin import ajax_functions
import logging
from web_admin.api_settings import UPDATE_CAMPAIGNS
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from django.contrib import messages
import json


def active(request, campaign_id):
    # if not check_permissions_by_user(request.user, 'CAN_SUSPEND_CLIENTS'):
    #     return

    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info('========== Start active campaign ==========')
    url = settings.DOMAIN_NAMES + UPDATE_CAMPAIGNS.format(bak_rule_id=campaign_id)
    params = {
        'is_active': True,
    }
    result = ajax_functions._put_method(request, url, "", logger, params)
    logger.info('========== Finish active campaign ==========')
    return result
