import logging
from django.conf import settings
from web_admin import api_settings, setup_logger
from web_admin import ajax_functions
from web_admin.restful_helper import RestfulHelper
from authentications.utils import get_correlation_id_from_username


def suspend(request, service_id):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info('========== Start suspending service ==========')
    url = settings.DOMAIN_NAMES + api_settings.SERVICE_URL.format(service_id)

    url_get_detail = api_settings.SERVICE_DETAIL_URL.format(service_id)
    success, status_code, status_message, data = RestfulHelper.send\
        ("GET", url_get_detail, {}, request,"getting service detail")
    if success :
        params = {
            'status': 0,
            'service_group_id': data['service_group_id'],
            'currency': data['currency'],
            'description': data['description'],
            'service_name': data['service_name']
        }

    result = ajax_functions._put_method(request, url, "", logger, params)
    logger.info('========== Finish suspending service ==========')
    return result
