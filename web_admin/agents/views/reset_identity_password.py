from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect

from web_admin import api_settings
from web_admin import ajax_functions
import logging
from web_admin.utils import setup_logger
from authentications.utils import get_correlation_id_from_username,check_permissions_by_user

# logger = logging.getLogger(__name__)


def reset_password(request, agent_id, identity_id):

    if not check_permissions_by_user(request.user, 'CAN_RESETPASSWORD_AGENT'):
        return

    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info('========== Start reset password==========')
    url = settings.DOMAIN_NAMES + api_settings.AGENT_IDENTITY_RESET_PASSWORD.format(agent_id, identity_id)
    params = {}
    result = ajax_functions._post_method(request, url, "", logger, params, timeout=settings.GLOBAL_TIMEOUT)
    logger.info('========== Finish reset password ==========')
    return result
