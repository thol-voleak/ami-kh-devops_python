import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from web_admin.mixins import GetChoicesMixin
from web_admin.restful_methods import RESTfulMethods
from web_admin.api_settings import GET_AGENT_BALANCE_BY_CURRENCY
from web_admin.api_settings import COMPANY_BALANCE_HISTORY
from web_admin.api_settings import COMPANY_BALANCE_ADD
from web_admin.api_settings import GET_AGET_BALANCE
from web_admin import api_settings
logger = logging.getLogger(__name__)


class CompanyBalanceView(TemplateView, GetChoicesMixin, RESTfulMethods):
    template_name = "company_balance.html"
    company_agent_id = 1

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name,
                      self._build_context(request)
                       )

    def post(self, request, *args, **kwargs):
        new_company_balance = request.POST.get('new_company_balance')
        amount = request.POST.get('adding_balance')
        string_amount = amount

        if isinstance(amount, str):
            amount = amount.replace(',', '')
        currency = request.POST.get('currency')

        data = {'amount': amount}

        response, success = self._add_company_balance(currency, data)

        if success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Added balance successfully'
            )
            return redirect(request.META['HTTP_REFERER'])
        else:
            messages.add_message(
                request,
                messages.ERROR,
                response
            )
            context = self._build_context(request)
            context['new_company_balance'] = new_company_balance
            context['string_amount'] = string_amount
            context['selected_currency'] = currency
            return render(request, self.template_name, context)


    def _get_total_initial_company_balance(self, currency):
        url = GET_AGENT_BALANCE_BY_CURRENCY.format(
            agent_id=self.company_agent_id,
            currency=currency)
        func_description = "Getting total initial balance by username: {} \
        ,agent id: {} and currency: {}".format(self.request.user.username,
                                               self.company_agent_id,
                                               currency, )
        return self._get_method(api_path=url,
                                func_description=func_description,
                                logger=logger,
                                is_getting_list=False)

    def _get_new_company_balance(self, data):
        def calculate_balance_after_change(x):
            x['balance_after_change'] = x['balance_before_change'] + x['changed_amount']
            return x

        return map(calculate_balance_after_change, data)

    def _get_company_balance_history(self, currency):
        url = COMPANY_BALANCE_HISTORY + currency
        return self._get_method(api_path=url,
                                func_description="company balance list by user",
                                logger=logger,
                                is_getting_list=True)

    def _add_company_balance(self, currency, body):
        url = COMPANY_BALANCE_ADD + currency
        return self._post_method(api_path=url,
                                          func_description="company balance by user",
                                          logger=logger,
                                          params=body)


    def _get_currency_choices_by_agent(self, agent_id):
        url = GET_AGET_BALANCE.format(agent_id)
        data, success = self._get_method(api_path=url,
                                         func_description="currency list by agent",
                                         logger=logger,
                                         is_getting_list=True)
        if success:
            currency_list = [i['currency'] for i in data]
            return currency_list, True
        else:
            return data, True

    def _get_currency_choices_list(self):
        url = api_settings.GET_ALL_CURRENCY_URL
        logger.info('Get currency choice list from backend')
        data, success = self._get_method(api_path=url,
                                         func_description="currency choice list",
                                         logger=logger,
                                         is_getting_list=False)
        if success:
            value = data.get('value','')
            if isinstance(value, str):
                currency_list = map(lambda x: x.split('|'), value.split(','))
            else:
                currency_list = []
            result = currency_list, True
        else:
            result = data, False
        return result

    def _build_context(self, request):
        default_decimal = 1
        currency_choices, success_currency = self._get_currency_choices_by_agent(self.company_agent_id)
        if not success_currency:
            messages.add_message(
                request,
                messages.ERROR,
                message=currency_choices
            )
            currency_choices = []

        currency_list, success_currency = self._get_currency_choices_list()
        if not success_currency:
            messages.add_message(
                request,
                messages.ERROR,
                message=currency_list
            )
            currency_list = []

        currency_list = list(filter(lambda x: x[0] in currency_choices, currency_list))
        if currency_list:
            currency = request.GET.get('currency', currency_list[0][0])
            decimal = list(filter(lambda x: x[0] == currency, currency_list))[0][1]
        else:
            currency, decimal = '', default_decimal

        totalData, success_total_balance = self._get_total_initial_company_balance(currency)

        if not success_total_balance:
            messages.add_message(
                request,
                messages.ERROR,
                message=totalData
            )
            totalData = {}

        data, success_balance = self._get_company_balance_history(currency)
        if success_balance:
            data = self._get_new_company_balance(data)
        else:
            messages.add_message(
                request,
                messages.ERROR,
                message=data
            )
            data = []

        return {'objects': list(data),
                       'currency_list': currency_list,
                       'decimal': decimal,
                       'total_balance': totalData}

company_balance = login_required(CompanyBalanceView.as_view(), login_url='authentications:login')
