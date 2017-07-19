from web_admin import api_settings, setup_logger, RestFulClient


class SystemUserClient:
    @classmethod
    def search_system_user(cls, headers=None, logger=None, username=None, email=None, user_id=None):
        params = {}

        if username is not '' and username is not None:
            params['username'] = username
        if email is not '' and email is not None:
            params['email'] = email
        if user_id is not '' and user_id is not None:
            params['user_id'] = user_id

        is_success, status_code, status_message, data = RestFulClient.post(api_settings.SEARCH_SYSTEM_USER,
                                                                           headers, logger, params)

        return status_code, status_message, data
