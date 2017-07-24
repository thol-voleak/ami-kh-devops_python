from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger
from web_admin.restful_methods import RESTfulMethods
from web_admin.api_settings import GET_ALL_CURRENCY_URL, GET_ALL_PRELOAD_CURRENCY_URL

from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class ListView(TemplateView, RESTfulMethods):
    group_required = "SYS_VIEW_CURRENCY"
    login_url = 'authentications:login'
    raise_exception = False

    template_name = "currencies/currencies_list.html"
    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = self.get_currencies_list()
        preload_data = self.get_preload_currencies_dropdown()
        refined_data = _refine_data(data)
        result = {
            'preload_data': preload_data,
            'data': refined_data,
            'msg': self.request.session.pop('client_update_msg', None)
        }
        return result

    def get_currencies_list(self):
        url = GET_ALL_CURRENCY_URL
        data, success = self._get_method(api_path=url,
                                         func_description="currency list",
                                         logger=logger,
                                         is_getting_list=True)
        return data

    def get_preload_currencies_dropdown(self):
        url = GET_ALL_PRELOAD_CURRENCY_URL
        data, success = self._get_method(api_path=url,
                                         func_description="preload currency list",
                                         logger=logger,
                                         is_getting_list=True)
        return data


def _refine_data(data):
    value = data.get('value', '')
    if value != '' and value is not None:
        currencies = value.split(',')
    else:
        return []
    currencyList = []

    for currency in currencies:
        name = currency.split('|')
        currencyList.append({'currency': name[0],
                             'decimal': name[1],
                             'last_update_timestamp': data['last_update_timestamp'],
                             'last_update_by_user_id': data['last_update_by_user_id']})
    return currencyList
