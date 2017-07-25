from braces.views import GroupRequiredMixin

from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger
from web_admin.restful_methods import RESTfulMethods
from web_admin.api_settings import CREATE_COMPANY_BALANCE
from web_admin.api_settings import GET_ALL_CURRENCY_URL
from web_admin.api_settings import GET_AGENT_BALANCE

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView

import logging
import copy

logger = logging.getLogger(__name__)


class CompanyBalanceView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "SYS_VIEW_COMPANY_BALANCE"
    login_url = 'web:permission_denied'
    raise_exception = False

    template_name = "currencies/initial_company_balance.html"
    company_agent_id = 1

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CompanyBalanceView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        currencies, success = self._get_currencies_list()
        if not success:
            messages.add_message(
                self.request,
                messages.ERROR,
                message=currencies
            )
            currencies = []

        agent_balance_list, success = self._get_agent_balances(self.company_agent_id)
        if not success:
            messages.add_message(
                self.request,
                messages.ERROR,
                message=agent_balance_list
            )
            agent_balance_list = []

        balance_list = []
        for item in agent_balance_list:
            balance_list.append(self.getUpdatedItem(item, currencies))

        result = {'currencies': currencies, 'agent_balance_list': balance_list}
        return result

    def getUpdatedItem(self, item, currencies):
        newItem = copy.deepcopy(item)
        for currency in currencies:
            if currency[0] == item.get("currency", ""):
                newItem["decimal"] = int(currency[1])
                return newItem

    def post(self, request, *args, **kwargs):
        currency = request.POST.get('currency')
        param = {'currency': currency}

        url = CREATE_COMPANY_BALANCE
        data, success = self._post_method(api_path=url,
                                          func_description="create company balance",
                                          params=param )
        if success:
            return redirect('balances:initial_company_balance')
        else:
            messages.add_message(
                request,
                messages.ERROR,
                message=data
            )
            currencies, success = self._get_currencies_list()
            if not success:
                messages.add_message(
                    request,
                    messages.ERROR,
                    message=currencies
                )
                currencies = []

            agent_balance_list, success = self._get_agent_balances(self.company_agent_id)
            if not success:
                messages.add_message(
                    self.request,
                    messages.ERROR,
                    message=agent_balance_list
                )
                agent_balance_list = []

            balance_list = []
            for item in agent_balance_list:
                balance_list.append(self.getUpdatedItem(item, currencies))

            context = {'currencies': currencies, 'agent_balance_list': balance_list, 'selected_currency': currency}
            return render(request, self.template_name, context)

    def _get_currencies_list(self):
        url = GET_ALL_CURRENCY_URL
        data, success = self._get_method(api_path=url,
                                         func_description="currency list from backend",
                                         is_getting_list=True)
        if success:
            value = data.get('value', '')
            currency_list = [i.split('|') for i in value.split(',')]
            return currency_list, True
        else:
            return data, False

    def _get_agent_balances(self, agent_id):
        url = GET_AGENT_BALANCE
        body = {'user_id' : agent_id}
        return self._post_method(api_path=url,func_description="agent balances",params=body)
