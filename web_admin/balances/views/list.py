from django.views.generic.base import TemplateView
from django.conf import settings
import requests, random, string

from authentications.models import *

import logging, datetime

logger = logging.getLogger(__name__)


class ListView(TemplateView):
    template_name = "currencies/currencies_list.html"

    def get_context_data(self, **kwargs):
        logger.info('========== Start get Currency List ==========')
        data = self.get_currencies_list()
        refined_data = _refine_data(data)
        logger.info('========== Finished get Currency List ==========')
        result = {'data': refined_data,
                'msg': self.request.session.pop('client_update_msg', None)}
        return result

    def get_currencies_list(self):
        client_id = settings.CLIENTID
        client_secret = settings.CLIENTSECRET
        url = settings.GET_ALL_CURRENCY_URL
        correlation_id = ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

        auth = Authentications.objects.get(user=self.request.user)
        access_token = auth.access_token

        headers = {
            'content-type': 'application/json',
            'correlation-id': correlation_id,
            'client_id': client_id,
            'client_secret': client_secret,
            'Authorization': 'Bearer ' + access_token,
        }
        logger.info('Getting currency list from backend')
        response = requests.get(url, headers=headers, verify=False)
        json_data = response.json()
        logger.info("Received data with response is {}".format(json_data))
        data = json_data.get('data')
        if response.status_code == 200:
            if (data is not None) and (len(data) > 0):
                return data

        raise Exception("{}".format(json_data["message"]))


def _refine_data(data):

    if (data['last_update_timestamp'] is not None) and (data['last_update_timestamp'] != "null"):
        last_update_timestamp = data['last_update_timestamp'] / 1000.0
        data['last_update_timestamp'] = datetime.datetime.fromtimestamp(float(last_update_timestamp)).strftime(
            '%d-%m-%Y %H:%M %p')

    currencies = data['value'].split(',')
    currencyList = []

    for currency in currencies:
        name = currency.split('|')
        currencyList.append({'currency':name[0],
                             'decimal': name[1],
                         'last_update_timestamp':data['last_update_timestamp'],
                         'last_update_by_user_id':data['last_update_by_display_name']})
    return currencyList