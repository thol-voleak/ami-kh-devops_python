import logging
from web_admin import api_settings, setup_logger
from web_admin import ajax_functions
from authentications.utils import get_correlation_id_from_username
import json


def get_agent_detail(request, agent_id):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info('========== Start to get agent detail ==========')
    data = get_agent_info(request,agent_id)
    data = data.content.decode('utf-8').replace('\0', '')
    data = json.loads(data);
    logger.info('========== Finish getting agent detail ==========')

    return data.get('data').get('agents')[0]


def get_agent_info(request, agent_id):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info('========== Start to call get agent detail ==========')
    body = {'id': agent_id}
    result = ajax_functions._post_method(request, api_settings.AGENT_DETAIL_PATH, "", logger, body)
    logger.info('========== Finish getting agent detail ==========')
    return result