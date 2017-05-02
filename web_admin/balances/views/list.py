import datetime
import logging
import time

import requests
from django.conf import settings
from django.views.generic.base import TemplateView

from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header

logger = logging.getLogger(__name__)


class ListView(TemplateView):
    template_name = "currencies/currencies_list.html"

    def get_context_data(self, **kwargs):
        logger.info('========== Start get Currency List ==========')
        data = self.get_currencies_list()
        preload_data = self.get_preload_currencies_dropdown()
        refined_data = _refine_data(data)
        logger.info('========== Finished get Currency List ==========')
        result = {'preload_data': preload_data,
                'data': refined_data,
                'msg': self.request.session.pop('client_update_msg', None)}
        return result

    def get_currencies_list(self):
        url = settings.GET_ALL_CURRENCY_URL

        logger.info("Getting currency list from backend with {} url".format(url))
        start_date = time.time()
        response = requests.get(url, headers=get_auth_header(self.request.user),
                                verify=settings.CERT)
        done = time.time()
        json_data = response.json()
        logger.info("Response time for get currency list is {} sec.".format(done - start_date))
        logger.info("Received data with response is {}".format(json_data))
        data = json_data.get('data')
        if response.status_code == 200:
            if (data is not None) and (len(data) > 0):
                return data

        if json_data["status"]["code"] == "access_token_expire":
            raise InvalidAccessToken(json_data["status"]["message"])
        else:
            raise Exception("{}".format(json_data["status"]["message"]))

    def get_preload_currencies_dropdown(self):
        url = settings.GET_ALL_PRELOAD_CURRENCY_URL

        logger.info("Getting preload currency list from backend with {} url".format(url))
        start_date = time.time()
        response = requests.get(url, headers=get_auth_header(self.request.user),
                                verify=settings.CERT)
        done = time.time()
        json_data = response.json()
        logger.info("Response time for get preload currency list is {} sec.".format(done - start_date))
        data = json_data.get('data')
        if response.status_code == 200:
            if (data is not None) and (len(data) > 0):
                logger.info("Received {} preload currencies".format(len(json_data['data'])))
                return data

        if json_data["status"]["code"] == "access_token_expire":
            raise InvalidAccessToken(json_data["status"]["message"])
        else:
            raise Exception("{}".format(json_data["status"]["message"]))


def _refine_data(data):
    currencies = data['value'].split(',')
    currencyList = []

    for currency in currencies:
        name = currency.split('|')
        currencyList.append({'currency':name[0],
                             'decimal': name[1],
                         'last_update_timestamp':data['last_update_timestamp'],
                         'last_update_by_user_id':data['last_update_by_user_id']})
    return currencyList
