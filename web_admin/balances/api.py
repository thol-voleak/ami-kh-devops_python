import logging
import requests
import time
import datetime
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse

from authentications.utils import get_auth_header
from web_admin import api_settings
from web_admin.utils import setup_logger

# logger = logging.getLogger(__name__)


class BalanceApi():

    def add(request, currency):
        logger = logging.getLogger(__name__)
        logger = setup_logger(request, logger)
        logger.info('========== Start add currency ==========')

        url = settings.DOMAIN_NAMES + api_settings.ADD_CURRENCY_URL.format(currency)
        logger.info("Add currency by {} user id".format(request.user.username))
        logger.info("Add currency from backend with {} url".format(url))

        params = {
            "value": currency
        }
        logger.info("Add currency from backend with {} request body".format(params))
        start = time.time()
        response = requests.put(url, headers=get_auth_header(request.user),
                                json=params, verify=settings.CERT)
        finish = time.time()
        logger.info('Response_code: {}'.format(response.status_code))
        logger.info('Response_content: {}'.format(response.text))
        logger.info('Response_time: {}'.format(finish - start))

        response_json = response.json()
        status = response_json.get('status', {})
        code = status.get('code', '')

        ajax_code = 0
        message = status.get('message', 'Something went wrong.')
        if code in ['access_token_expire', 'access_token_not_found', 'invalid_access_token']:
            logger.info("{} for {} username".format(message, request.user))
            messages.add_message(request, messages.INFO, str('session_is_expired'))
            ajax_code = 1
            logger.info('========== Finish add currency ==========')
            return JsonResponse({"status": ajax_code, "msg": message})

        currencyList = []
        if status['code'] == "success":
            ajax_code = 2
            logger.info("Currency was added")
            logger.info('========== Finish add currency ==========')
            currencyList = refine_data(response_json['data'])
        else:
            ajax_code = 3
            logger.info('========== Finish add currency ==========')

        return JsonResponse({"status": ajax_code, "msg": message, "data": currencyList})


def refine_data(data):

    currencies = data['value'].split(',')
    currencyList = []

    for currency in currencies:
        name = currency.split('|')
        currencyList.append({'currency': name[0],
                             'decimal': name[1],
                             'last_update_timestamp': data['last_update_timestamp'],
                             'last_update_by_user_id': data['last_update_by_user_id']})
    return currencyList
