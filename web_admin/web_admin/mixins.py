from authentications.utils import get_auth_header
from web_admin import api_settings
from web_admin.restful_methods import RESTfulMethods

from multiprocessing.pool import ThreadPool

import logging

logger = logging.getLogger(__name__)


class GetChoicesMixin(RESTfulMethods):
    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers

    def _get_currency_choices(self):
        url = api_settings.GET_ALL_CURRENCY_URL
        logger.info('Get currency choice list from backend')
        data, success = self._get_method(api_path=url,
                                         func_description="currency choice list",
                                         logger=logger,
                                         is_getting_list=False)
        if success:
            value = data.get('value', '')
            if isinstance(value, str):
                currency_list = map(lambda x: x.split('|'), value.split(','))
            else:
                currency_list = []
            result = currency_list, True
        else:
            result = [], False
        return result

    def _get_service_group_choices(self):
        url = api_settings.SERVICE_GROUP_LIST_URL
        logger.info('Get services group list from backend')
        return self._get_method(api_path=url,
                                func_description="currency choice list",
                                logger=logger,
                                is_getting_list=False)

    def _get_service_group_and_currency_choices(self):
        pool = ThreadPool(processes=1)
        async_result = pool.apply_async(self._get_currency_choices)
        service_groups, success_service = self._get_service_group_choices()
        currencies, success_currency = async_result.get()
        if success_currency and success_service:
            return {
                       'currencies': currencies,
                       'service_groups': service_groups,
                   }, True
        return None, False
