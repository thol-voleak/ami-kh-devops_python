import json
import logging
import requests
import time
import random
import string
import datetime

from django.conf import settings
from django.http import HttpResponse
from django.http import JsonResponse

from authentications.models import Authentications

logger = logging.getLogger(__name__)


class BalanceApi():

    def add(request, currency):
        logger.info('========== Start add currency ==========')

        url = settings.ADD_CURRENCY_URL.format(currency)
        auth = Authentications.objects.get(user=request.user)
        access_token = auth.access_token

        correlation_id = ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

        headers = {
            'content-type': 'application/json',
            'correlation-id': correlation_id,
            'client_id': settings.CLIENTID,
            'client_secret': settings.CLIENTSECRET,
            'Authorization': 'Bearer {}'.format(access_token),
        }

        logger.info("Add currency by {} user id".format(auth.user))
        logger.info("Add currency from backend with {} url".format(url))

        params = {
            "value": currency
        }
        logger.info("Add currency from backend with {} request body".format(params))
        start_date = time.time()
        response = requests.put(url, headers=headers, json=params, verify=False)
        logger.info(response)
        done = time.time()
        response_json = response.json()

        logger.info("Response time for add currency is {} sec.".format(done - start_date))
        logger.info("Received data with response is {}".format(response_json))

        status = response_json['status']
        if status['code'] == "success":
            logger.info("Currency was added")
            logger.info('========== Finish add currency ==========')
            data = refine_data(response_json['data'])
            return HttpResponse(status=200, content=data)
        else:
            logger.info("Error add currency")
            logger.info('========== Finish add currency ==========')
            return HttpResponse(status=500, content=response)


def refine_data(data):

    if (data['last_update_timestamp'] is not None) and (data['last_update_timestamp'] != "null"):
        last_update_timestamp = data['last_update_timestamp'] / 1000.0
        data['last_update_timestamp'] = datetime.datetime.fromtimestamp(float(last_update_timestamp)).strftime(
                '%d-%m-%Y %H:%M %p')

    currencies = data['value'].split(',')
    currencyList = []

    for currency in currencies:
        name = currency.split('|')
        currencyList.append({'currency': name[0],
                             'decimal': name[1],
                             'last_update_timestamp': data['last_update_timestamp'],
                             'last_update_by_user_id': data['last_update_by_user_id']})
    return JsonResponse(currencyList, safe=False)