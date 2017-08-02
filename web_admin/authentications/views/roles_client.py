from authentications.apps import InvalidAccessToken
from web_admin import RestFulClient, api_settings


class RolesClient:
    @classmethod
    def create_role(cls, headers, params, logger):
        is_success, status_code, status_message, data = RestFulClient.post(
            url=api_settings.CREATE_ROLE_PATH, headers=headers, loggers=logger, params=params
        )

        if not is_success:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                logger.info("{}".format(status_message))
                raise InvalidAccessToken(status_message)

        return is_success, status_code, status_message, data