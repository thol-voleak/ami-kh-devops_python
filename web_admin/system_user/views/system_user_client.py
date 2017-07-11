from web_admin import api_settings
from web_admin import setup_logger, RestFulClient


class SystemUserClient:
    @classmethod
    def search_system_user(cls, request, headers, logger, username, email, user_id):
        params = {}

        if username is not '' and username is not None:
            params['username'] = username
        if email is not '' and email is not None:
            params['email'] = email
        if user_id is not '' and user_id is not None:
            params['user_id'] = user_id

        is_success, status_code, status_message, data = RestFulClient.post(request,
                                                                           api_settings.SEARCH_SYSTEM_USER,
                                                                           headers, logger, params)

        return status_code, status_message, data