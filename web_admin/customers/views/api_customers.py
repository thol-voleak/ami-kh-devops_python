from web_admin import api_settings
from web_admin import ajax_functions
from web_admin.utils import setup_logger
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user

from django.conf import settings

import logging


def activate(request, customer_id):
    if not check_permissions_by_user(request.user, 'CAN_SUSPEND_CUSTOMER'):
        return

    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info('========== Start activating customer ==========')
    url = settings.DOMAIN_NAMES + api_settings.ACTIVATE_CUSTOMER.format(customer_id)
    params = {
        'is_suspended': 'false',
    }

    result = ajax_functions._put_method(request, url, "", logger, params)
    logger.info('========== Finish activating customer ==========')
    return result


def delete_customer(request, customer_id):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info('========== Start delete customer ==========')

    if request.method == 'POST':
        logger.info('Sending request to backend service')
        url = settings.DOMAIN_NAMES + api_settings.ADMIN_DELETE_CUSTOMER_URL.format(customer_id)

        result = ajax_functions._delete_method(request=request,
                                               api_path=url,
                                               func_description="",
                                               logger=logger)
        logger.info('========== Finish activating customer ==========')
        return result


def enable_device(request, customerId, deviceId):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info("Checking permission for [{}] username with [{}] permission".format(request.user, 'CAN_DISABLE_CUSTOMER_DEVICE'))
    if not check_permissions_by_user(request.user, 'CAN_DISABLE_CUSTOMER_DEVICE'):
        return {"status": 1, "msg": ''}
    logger.info('========== Start enable device ==========')
    url = settings.DOMAIN_NAMES + api_settings.CUSTOMER_DEVICE_STATUS_URL.format(deviceId)
    params = {
        'is_active': True,
    }

    result = ajax_functions._put_method(request, url, "", logger, params)
    logger.info('========== Finish enable device ==========')
    return result


def disable_device(request, customerId, deviceId):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info("Checking permission for [{}] username with [{}] permission".format(request.user, 'CAN_DISABLE_CUSTOMER_DEVICE'))
    if not check_permissions_by_user(request.user, 'CAN_DISABLE_CUSTOMER_DEVICE'):
        return {"status": 1, "msg": ''}
    logger.info('========== Start disable device ==========')
    url = settings.DOMAIN_NAMES + api_settings.CUSTOMER_DEVICE_STATUS_URL.format(deviceId)
    params = {
        'is_active': False,
    }

    result = ajax_functions._put_method(request, url, "", logger, params)
    logger.info('========== Finish disable device ==========')
    return result


def unbind_device(request, customerId, deviceId):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info("Checking permission for [{}] username with [{}] permission".format(request.user, 'CAN_UNBIND_CUSTOMER_DEVICE'))
    if not check_permissions_by_user(request.user, 'CAN_UNBIND_CUSTOMER_DEVICE'):
        return {"status": 1, "msg": ''}
    logger.info('========== Start delete device ==========')
    url = settings.DOMAIN_NAMES + api_settings.CUSTOMER_DEVICE_DELETE_URL.format(deviceId)

    result = ajax_functions._delete_method(request, url, "", logger)
    logger.info('========== Finish delete device ==========')
    return result


def grant_channel_access(request, customerId, channelId):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info("Checking permission for [{}] username with [{}] permission".format(request.user, 'CAN_BLOCK_CUSTOMER_CHANNELS'))
    if not check_permissions_by_user(request.user, 'CAN_BLOCK_CUSTOMER_CHANNELS'):
        return {"status": 1, "msg": ''}
    logger.info('========== Start grant access to channel ==========')
    url = settings.DOMAIN_NAMES + api_settings.CUSTOMER_CHANNEL_GRANT_URL.format(channelId)
    params = {
        'user_id': customerId,
        'user_type': {
            "id": 1,
            'name': 'customer'
        }
    }

    result = ajax_functions._post_method(request, url, "", logger, params)
    logger.info('========== Finish grant access to channel ==========')
    return result


def revoke_channel_access(request, customerId, channelId):
    logger = logging.getLogger(__name__)
    correlation_id = get_correlation_id_from_username(request.user)
    logger = setup_logger(request, logger, correlation_id)
    logger.info("Checking permission for [{}] username with [{}] permission".format(request.user, 'CAN_BLOCK_CUSTOMER_CHANNELS'))
    if not check_permissions_by_user(request.user, 'CAN_BLOCK_CUSTOMER_CHANNELS'):
        return {"status": 1, "msg": ''}
    logger.info('========== Start block access to channel ==========')
    url = settings.DOMAIN_NAMES + api_settings.CUSTOMER_CHANNEL_REVOKE_URL.format(channelId)
    params = {
        'user_id': customerId,
        'user_type': {
            "id": 1,
            'name': 'customer'
        }
    }

    result = ajax_functions._post_method(request, url, "", logger, params)
    logger.info('========== Finish block access to channel ==========')
    return result