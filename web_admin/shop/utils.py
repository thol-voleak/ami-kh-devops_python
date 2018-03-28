from web_admin.restful_client import RestFulClient
from web_admin.api_logger import API_Logger
from web_admin import api_settings


def get_all_shop_type(self):
    api_path = api_settings.GET_LIST_SHOP_TYPE
    success, status_code, status_message, data = RestFulClient.post(
        url=api_path,
        headers=self._get_headers(),
        loggers=self.logger)

    data = data or {}
    API_Logger.post_logging(loggers=self.logger,
                            response=data.get('shop_types', []),
                            status_code=status_code,
                            is_getting_list=True,
                            params={'paging': False, 'is_deleted': False})
    return data.get('shop_types', [])

def get_all_shop_category(self):
    api_path = api_settings.GET_LIST_SHOP_CATEGORIES
    success, status_code, status_message, data = RestFulClient.post(
        url=api_path,
        headers=self._get_headers(),
        loggers=self.logger)

    data = data or {}
    API_Logger.post_logging(loggers=self.logger,
                            response=data.get('shop_categories', []),
                            status_code=status_code,
                            is_getting_list=True,
                            params={'paging': False, 'is_deleted': False})
    return data.get('shop_categories', [])

def get_system_country():
    # TODO
    return "VN"