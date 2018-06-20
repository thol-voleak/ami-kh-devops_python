from web_admin import api_settings, setup_logger, RestFulClient


class SystemUserClient:
    @classmethod
    def search_system_user(cls, headers=None, logger=None, username=None, email=None, user_id=None, status=None, paging=None, page_index=None):
        params = {}

        if username is not '' and username is not None:
            params['username'] = username
        if email is not '' and email is not None:
            params['email'] = email
        if user_id is not '' and user_id is not None:
            params['user_id'] = user_id
        if status is not None:
            if status == 'Active':
                params['is_suspended'] = False
            if status == 'Suspended':
                params['is_suspended'] = True
        if paging is not '' and paging is not None:
            params['paging'] = paging
        if page_index and page_index.isdigit():
            params['page_index'] = int(page_index)

        is_success, status_code, status_message, data = RestFulClient.post(api_settings.SEARCH_SYSTEM_USER,
                                                                           headers, logger, params)
        return is_success, status_code, status_message, data
