from django.views.generic.base import TemplateView
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render

import requests
import time
import logging
import datetime

from authentications.apps import InvalidAccessToken
from web_admin.get_header_mixins import GetHeaderMixin

logger = logging.getLogger(__name__)


class CompanyBalanceView(TemplateView, GetHeaderMixin):
    template_name = "currencies/setup_company_balance.html"
    company_agent_id = 1

    def get_context_data(self, **kwargs):
        logger.info('========== Start get Currency List ==========')
        currencies = self._get_currencies_list()
        agent_balance_list = self._get_agent_balances(self.company_agent_id)
        balance_list = self._get_date_format(agent_balance_list)
        logger.info('========== Finished get Currency List ==========')
        result = {'currencies': currencies, 'agent_balance_list': balance_list}
        return result

    def post(self, request, *args, **kwargs):
        logger.info('========== Start create company balance ==========')
        currency = request.POST.get('currency')
        headers = self._get_headers()
        url = settings.CREATE_COMPANY_BALANCE.format(currency)

        start_date = time.time()
        response = requests.post(url, headers=headers, verify=False)
        done = time.time()
        logger.info("Response time for add company balance is {} sec.".format(done - start_date))

        json_data = response.json()
        if response.status_code == 200:
            if json_data["status"]["code"] == "success":
                currencies = self.get_currencies_list()
                agent_balance_list = self._get_agent_balances(self.company_agent_id)
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'Added company balance with {} currency successfully'.format(currency)
                )
                logger.info('========== Finished create company balance ==========')
                return render(request, self.template_name,
                              {'currencies': currencies, 'agent_balance_list': agent_balance_list})
        else:
            if json_data["status"]["code"] == "access_token_expire":
                raise InvalidAccessToken(json_data["status"]["message"])
            else:
                raise Exception("{}".format(json_data["status"]["message"]))

    def _get_currencies_list(self):
        headers = self._get_headers()
        url = settings.GET_ALL_CURRENCY_URL
        logger.info("Getting currency list from backend with {} url".format(url))

        start_date = time.time()
        response = requests.get(url, headers=headers, verify=False)
        done = time.time()
        logger.info("Response time for get currency list is {} sec.".format(done - start_date))

        json_data = response.json()
        logger.info("Received data with response is {}".format(json_data))
        if response.status_code == 200:
            value = json_data.get('data', {}).get('value', '')
            currency_list = map(lambda x: x.split('|'), value.split(','))
            return currency_list
        else:
            if json_data["status"]["code"] == "access_token_expire":
                raise InvalidAccessToken(json_data["status"]["message"])
            else:
                raise Exception("{}".format(json_data["status"]["message"]))

    def _get_agent_balances(self, agent_id):
        url = settings.GET_AGET_BALANCE.format(agent_id)
        headers = self._get_headers()
        start_date = time.time()
        response = requests.get(url, headers=headers, verify=False)
        done = time.time()
        logger.info("Response time for get agent balances is {} sec.".format(done - start_date))

        json_data = response.json()
        if response.status_code == 200:
            data = json_data.get('data', {})
            return data
        else:
            if json_data["status"]["code"] == "access_token_expire":
                raise InvalidAccessToken(json_data["status"]["message"])
            else:
                raise Exception("{}".format(json_data["status"]["message"]))

    def _get_date_format(self, data):
        for item in data:
            if (item.get('last_update') is not None) and (item['last_update'] != "null"):
                last_update = item['last_update'] / 1000.0
                item['last_update'] = datetime.datetime.fromtimestamp(float(last_update)).strftime(
                    '%d-%m-%Y %H:%M %p')
        return data
