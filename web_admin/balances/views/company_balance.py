import logging
import copy
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods
from web_admin.api_settings import CREATE_COMPANY_BALANCE
from web_admin.api_settings import GET_ALL_CURRENCY_URL
from web_admin.api_settings import GET_AGET_BALANCE
from django.contrib import messages
from django.shortcuts import redirect, render
logger = logging.getLogger(__name__)

class CompanyBalanceView(TemplateView, RESTfulMethods):
    template_name = "currencies/initial_company_balance.html"
    company_agent_id = 1

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

        url = CREATE_COMPANY_BALANCE.format(currency)
        data, success = self._post_method(api_path= url,
                                          func_description="create company balance",
                                          logger=logger)
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
                                         logger=logger,
                                         is_getting_list= True)
        if success:
            value = data.get('value', '')
            currency_list = [i.split('|') for i in value.split(',')]
            return currency_list, True
        else:
            return data, False

    def _get_agent_balances(self, agent_id):
        url = GET_AGET_BALANCE.format(agent_id)
        return self._get_method(api_path=url,
                                         func_description="agent balances",
                                         logger=logger,
                                         is_getting_list=True)

            
        
        
        



