import logging

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic.base import TemplateView

from web_admin.mixins import GetChoicesMixin
from web_admin.utils import format_date_time

logger = logging.getLogger(__name__)


class CompanyBalanceView(TemplateView, GetChoicesMixin):
    template_name = "company_balance.html"

    def get(self, request, *args, **kwargs):
        currency_list, success_currency = self._get_currency_choices()
        currency_list = list(currency_list)
        currency = request.GET.get('currency', currency_list[0][0])

        logger.info('========== Start get Company Balance List ==========')
        data, success_balance = self._get_company_balance_history(currency)
        logger.info('========== Finished get Company Balance List ==========')

        if success_balance:
            data = format_date_time(data)
            data = self._get_new_company_balance(data)

        return render(request, self.template_name,
                      {'objects': data, 'currency_list': currency_list})

    def _get_new_company_balance(self, data):
        def calculate_balance_after_change(x):
            x['balance_after_change'] = x['balance_before_change'] + x['changed_amount']
            return x
        return map(calculate_balance_after_change, data)

    def _get_company_balance_history(self, currency):
        logger.info("Getting company balance list by user: {}".format(self.request.user.username))

        url = settings.COMPANY_BALANCE_HISTORY + currency
        logger.info("Request url: {}".format(url))

        response = requests.get(url, headers=self._get_headers(), verify=False)
        logger.info("Received response with status {} of user id {}".format(
            response.status_code,
            self.request.user.id,
        ))

        json_data = response.json()
        if response.status_code == 200:
            data = json_data.get('data')
            logger.info("Total count of Agent Types is {}".format(len(data)))
            return data, True
        else:
            logger.info("Response content is {}".format(response.content))
            return [], False


company_balance = login_required(CompanyBalanceView.as_view(), login_url='login')
