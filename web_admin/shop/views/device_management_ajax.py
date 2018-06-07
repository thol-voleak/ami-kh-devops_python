from web_admin import api_settings
from web_admin import ajax_functions
from web_admin.utils import setup_logger
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from shop.utils import get_channel_detail

from django.conf import settings

import logging


def grant_channel_access(request, shop_id, channel_id):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info("Checking permission for [{}] username with [{}] permission".format(request.user,
                                                                                    'CAN_BLOCK_AGENT_CHANNELS'))
    if not check_permissions_by_user(request.user, 'CAN_BLOCK_AGENT_CHANNELS'):
        return {"status": 1, "msg": ''}
    logger.info('========== Start grant access to channel ==========')
    url = settings.DOMAIN_NAMES + api_settings.CHANNEL_GRANT_PERMISSION.format(channel_id=channel_id)
    params = {
        'shop_id': shop_id,
        'user_type': {
            'id': 2,
            'name': 'agent'
        }
    }

    result = ajax_functions._post_method(request, url, "", logger, params)
    logger.info('========== Finish grant access to channel ==========')

    return result

def revoke_channel_access(request, shop_id, channel_id):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info("Checking permission for [{}] username with [{}] permission".format(request.user,
                                                                                    'CAN_BLOCK_AGENT_CHANNELS'))
    if not check_permissions_by_user(request.user, 'CAN_BLOCK_AGENT_CHANNELS'):
        return {"status": 1, "msg": ''}
    logger.info('========== Start block access to channel ==========')
    url = settings.DOMAIN_NAMES + api_settings.CHANNEL_REVOKE_PERMISSION.format(channel_id=channel_id)
    params = {
        'shop_id': shop_id,
        'user_type': {
            "id": 2,
            'name': 'agent'
        }
    }

    result = ajax_functions._post_method(request, url, "", logger, params)
    logger.info('========== Finish block access to channel ==========')
    return result

def disable_device(request, device_id):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info("Checking permission for [{}] username with [{}] permission".format(request.user, 'CAN_DISABLE_AGENT_DEVICE'))
    if not check_permissions_by_user(request.user, 'CAN_DISABLE_AGENT_DEVICE'):
        return {"status": 1, "msg": ''}
    logger.info('========== Start disable device ==========')
    url = settings.DOMAIN_NAMES + api_settings.UPDATE_AGENT_DEVICE_STATUS.format(device_id=device_id)
    params = {
        'is_active': False,
    }

    result = ajax_functions._put_method(request, url, "", logger, params)
    logger.info('========== Finish disable device ==========')
    return result

def enable_device(request, device_id):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info("Checking permission for [{}] username with [{}] permission".format(request.user, 'CAN_DISABLE_AGENT_DEVICE'))
    if not check_permissions_by_user(request.user, 'CAN_DISABLE_AGENT_DEVICE'):
        return {"status": 1, "msg": ''}
    logger.info('========== Start enable device ==========')
    url = settings.DOMAIN_NAMES + api_settings.UPDATE_AGENT_DEVICE_STATUS.format(device_id=device_id)
    params = {
        'is_active': True,
    }

    result = ajax_functions._put_method(request, url, "", logger, params)
    logger.info('========== Finish enable device ==========')
    return result


def unbind_device(request, device_id):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info("Checking permission for [{}] username with [{}] permission".format(request.user, 'CAN_UNBIND_AGENT_DEVICE'))
    if not check_permissions_by_user(request.user, 'CAN_UNBIND_AGENT_DEVICE'):
        return {"status": 1, "msg": ''}
    logger.info('========== Start delete device ==========')
    url = settings.DOMAIN_NAMES + api_settings.DELETE_AGENT_DEVICE.format(device_id=device_id)

    result = ajax_functions._delete_method(request, url, "", logger)
    logger.info('========== Finish delete device ==========')
    return result