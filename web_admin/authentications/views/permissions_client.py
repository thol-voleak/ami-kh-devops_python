import logging

from authentications.apps import InvalidAccessToken
from web_admin import RestFulClient, api_settings

logger = logging.getLogger(__name__)


class PermissionsClient:
    @classmethod
    def create_permission(cls, headers, params, logger):
        is_success, status_code, status_message, data = RestFulClient.post(url=api_settings.CREATE_PERMISSION_PATH,
                                                                           loggers=logger, headers=headers,
                                                                           params=params)
        if not is_success:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                logger.info("{}".format(status_message))
                raise InvalidAccessToken(status_message)

        return is_success, status_code, status_message, data

    @classmethod
    def get_permissions(cls, headers, params, logger):
        is_success, status_code, status_message, permissions = RestFulClient.post(url=api_settings.PERMISSION_LIST,
                                                                                  headers=headers,
                                                                                  loggers=logger,
                                                                                  params=params)
        if not is_success:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                logger.info("{}".format(status_message))
                raise InvalidAccessToken(status_message)

        return is_success, status_code, status_message, permissions

    @classmethod
    def get_permission_detail(cls, headers, params, logger):
        is_success, status_code, status_message, data = RestFulClient.post(url=api_settings.PERMISSION_LIST,
                                                                           headers=headers,
                                                                           loggers=logger,
                                                                           params=params)
        if not is_success:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                logger.info("{}".format(status_message))
                raise InvalidAccessToken(status_message)

        if is_success and len(data) > 0:
            permission_detail = data[0]

        return is_success, status_code, status_message, permission_detail

    @classmethod
    def update_permission(cls, permission_id, headers, params, logger):
        url = api_settings.PERMISSION_DETAIL_PATH.format(permission_id=permission_id)

        is_success, status_code, status_message, data = RestFulClient.put(url=url,
                                                                          headers=headers,
                                                                          loggers=logger,
                                                                          params=params)
        if not is_success:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                logger.info("{}".format(status_message))
                raise InvalidAccessToken(status_message)

        return is_success, status_code, status_message, data

    @classmethod
    def delete_permission(cls, id, headers, logger):
        url = api_settings.PERMISSION_DETAIL_PATH.format(permission_id=id)
        is_success, status_code, status_message = RestFulClient.delete(url=url, headers=headers, loggers=logger)

        if not is_success:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                logger.info("{}".format(status_message))
                raise InvalidAccessToken(status_message)

        return is_success, status_code, status_message
