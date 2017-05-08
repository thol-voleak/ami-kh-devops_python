import logging

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView

from web_admin.mixins import GetChoicesMixin

logger = logging.getLogger(__name__)


class CompanyBalanceView(TemplateView, GetChoicesMixin):
    template_name = "company_balance.html"
    company_agent_id = 1

    def get(self, request, *args, **kwargs):
        logger.info('========== Start get Currency List ==========')
        default_decimal = 1

        currency_choices, success_currency = self._get_currency_choices_by_agent(self.company_agent_id)
        currency_list, success_currency = self._get_currency_choices()
        logger.info('========== Finished get Currency List ==========')

        currency_list = list(filter(lambda x: x[0] in currency_choices, currency_list))
        if currency_list:
            currency = request.GET.get('currency', currency_list[0][0])
            decimal = list(filter(lambda x: x[0] == currency, currency_list))[0][1]
        else:
            currency, decimal = '', default_decimal

        logger.info('========== Start get Company Balance List ==========')
        data, success_balance = self._get_company_balance_history(currency)
        logger.info('========== Finished get Company Balance List ==========')

        if success_balance:
            data = self._get_new_company_balance(data)

        logger.info('========== Start get Total Initial Company Balance ==========')
        totalData, success_total_balance = self._get_total_initial_company_balance(currency)
        logger.info('========== Finished get Total Initial Company Balance ==========')

        return render(request, self.template_name,
                      {'objects': list(data),
                       'currency_list': currency_list,
                       'decimal': decimal,
                       'total_balance': totalData})

    def post(self, request, *args, **kwargs):
        amount = request.POST.get('adding_balance')
        if isinstance(amount, str):
            amount = float(amount.replace(',', ''))
        currency = request.POST.get('currency')

        data = {'amount': amount}

        logger.info('========== Start adding company balance ==========')
        success = self._add_company_balance(currency, data)
        logger.info('========== Finished adding company balance ==========')

        if success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Added balance successfully'
            )
        else:
            messages.add_message(
                request,
                messages.error,
                'Something wrong happened'
            )

        return redirect(request.META['HTTP_REFERER'])

    def _get_total_initial_company_balance(self, currency):
        logger.info("Getting total initial balance by username: {}".format(self.request.user.username))
        logger.info("Getting total initial balance by agent id: {} and currency: {}".format(
            self.company_agent_id,
            currency,
        ))
        url = settings.GET_AGENT_BALANCE_BY_CURRENCY.format(agent_id=self.company_agent_id, currency=currency)
        logger.info("Request url: {}".format(url))

        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)
        logger.info("_get_total_initial_company_balance response with status {} of user id {}".format(
            response.status_code,
            self.request.user.id,
        ))

        json_data = response.json()
        if response.status_code == 200:
            data = json_data.get('data', {})
            return data, True
        else:
            logger.info("_get_total_initial_company_balance Response is {}".format(response.text))
            return {}, False

    def _get_new_company_balance(self, data):
        def calculate_balance_after_change(x):
            x['balance_after_change'] = x['balance_before_change'] + x['changed_amount']
            return x

        return map(calculate_balance_after_change, data)

    def _get_company_balance_history(self, currency):
        logger.info("Getting company balance list by user: {}".format(self.request.user.username))

        url = settings.COMPANY_BALANCE_HISTORY + currency
        logger.info("Request url: {}".format(url))

        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)
        logger.info("Received response with status {} of user id {}".format(
            response.status_code,
            self.request.user.id,
        ))

        json_data = response.json()
        if response.status_code == 200:
            data = json_data.get('data')
            logger.info("Total count of Company Balance is {}".format(len(data)))
            return data, True
        else:
            logger.info("_get_company_balance_history Response is {}".format(response.text))
            return [], False

    def _add_company_balance(self, currency, data):
        logger.info("Adding company balance by user {}".format(self.request.user.username))
        url = settings.COMPANY_BALANCE_ADD + currency
        logger.info("Request url: {}".format(url))

        logger.info("Request body: {}".format(data))
        response = requests.post(url, headers=self._get_headers(), json=data, verify=False)

        logger.info("Response content: {}".format(response.content))
        if response.status_code == 200:
            return True
        else:
            logger.info("_add_company_balance response with status {}".format(
                response.text))
            return False

    def _get_currency_choices_by_agent(self,agent_id):
        url = settings.GET_AGET_BALANCE.format(agent_id)
        logger.info('Getting currency list by agent')
        logger.info("Username: {}".format(self.request.user.username))
        logger.info('Request url: {}'.format(url))
        response = requests.get(url, headers=self._get_headers(), verify=settings.CERT)
        logger.info("Received response with status {}".format(response.status_code))

        if response.status_code == 200:
            json_data = response.json()
            data = json_data.get('data', {})
            currency_list = [x['currency'] for x in data]
            logger.info("Total count of Currency List is {}".format(len(currency_list)))
            return currency_list, True
        logger.info('_get_currency_choices_by_agent response: {}'.format(response.text))
        return [], False

company_balance = login_required(CompanyBalanceView.as_view(), login_url='login')
