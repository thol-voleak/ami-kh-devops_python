import logging
from django.conf import settings
from web_admin import api_settings, setup_logger
from web_admin import ajax_functions
from django.shortcuts import redirect, render
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
import json
from django.contrib import messages


def delete_relationship(request, relationship_id):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info("Checking permission for [{}] username with [{}] permission".format(request.user, 'CAN_DELETE_AGENT_RELATIONSHIP'))
    if not check_permissions_by_user(request.user, 'CAN_DELETE_AGENT_RELATIONSHIP'):
        return {"status": 1, "msg": ''}
    logger.info('========== Start delete relationship ==========')
    url = settings.DOMAIN_NAMES + api_settings.DELETE_RELATIONSHIP.format(relationship_id)

    result = ajax_functions._delete_method(request, url, "", logger)
    logger.info('========== Finish delete relationship ==========')
    return result


def share_benefit_relationship(request, relationship_id):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info("Checking permission for [{}] username with [{}] permission".format(request.user, 'CAN_SHARE_AGENT_BENEFIT'))
    if not check_permissions_by_user(request.user, 'CAN_SHARE_AGENT_BENEFIT'):
        return {"status": 1, "msg": ''}
    logger.info('========== Start share benefit relationship ==========')
    url = settings.DOMAIN_NAMES + api_settings.SHARE_BENEFIT_RELATIONSHIP.format(relationship_id)
    params = {
        "is_sharing_benefit": "true"
    }
    result = ajax_functions._put_method(request, url, "", logger, params)
    logger.info('========== Finish share benefit relationship ==========')
    return result


def stop_share_benefit_relationship(request, relationship_id):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info("Checking permission for [{}] username with [{}] permission".format(request.user, 'CAN_SHARE_AGENT_BENEFIT'))
    if not check_permissions_by_user(request.user, 'CAN_SHARE_AGENT_BENEFIT'):
        return {"status": 1, "msg": ''}
    logger.info('========== Start stop share benefit relationship ==========')
    url = settings.DOMAIN_NAMES + api_settings.SHARE_BENEFIT_RELATIONSHIP.format(relationship_id)
    params = {
        "is_sharing_benefit": "false"
    }
    result = ajax_functions._put_method(request, url, "", logger, params)
    logger.info('========== Finish stop share benefit relationship ==========')
    return result


def add_agent_relationship(request, agent_id):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info("Checking permission for [{}] username with [{}] permission".format(request.user, 'CAN_ADD_AGENT_RELATIONSHIP'))
    if not check_permissions_by_user(request.user, 'CAN_ADD_AGENT_RELATIONSHIP'):
        return {"status": 1, "msg": ''}
    logger.info('========== Start add agent relationship ==========')
    array_data = request.POST['relationship']
    data = json.loads(array_data)
    url = settings.DOMAIN_NAMES + api_settings.ADD_RELATIONSHIP
    if isinstance(data['main_id'], str):
        params = {
            "relationship_type_id": data['relationship_type_id'],
            "main_user": {
                "user_type": {
                    "id": 2,
                    "name": "agent"
                }
            },
            "sub_user": {
                "user_type": {
                    "id": 2,
                    "name": "agent"
                }
            }
        }
        result_fail = []
        params['main_user']['user_id'] = data['main_id']
        for sub_user in data['sub_id']:
            params['sub_user']['user_id'] = sub_user
            result = ajax_functions._post_method(request, url, "", logger, params)
            if result.status_code == 400:
                result_fail.append(sub_user)
    context = {'msg': 'test abcd', 'agent_id' : agent_id}
    return render(request, 'agents/management_relationship.html', context)
