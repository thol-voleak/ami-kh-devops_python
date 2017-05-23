import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic.base import TemplateView
from web_admin.mixins import GetChoicesMixin
from web_admin.restful_methods import *

logger = logging.getLogger(__name__)


class CompanyBalanceView(TemplateView, GetChoicesMixin, RESTfulMethods):
    template_name = "company_balance.html"
    company_agent_id = 1

    def get(self, request, *args, **kwargs):
        default_decimal = 1
        logger.info('========== Start get Currency List ==========')
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
        url = settings.GET_AGENT_BALANCE_BY_CURRENCY.format(
                                               agent_id=self.company_agent_id, 
                                               currency=currency)
        func_description = "Getting total initial balance by username: {} \
        ,agent id: {} and currency: {}".format(self.request.user.username,
                                               self.company_agent_id, 
                                               currency,)
        return self._get_method(api_path=url,
                                         func_description=func_description,
                                         logger=logger,
                                         is_getting_list= False)

    def _get_new_company_balance(self, data):
        def calculate_balance_after_change(x):
            x['balance_after_change'] = x['balance_before_change'] + x['changed_amount']
            return x

        return map(calculate_balance_after_change, data)

    def _get_company_balance_history(self, currency):
        url = settings.COMPANY_BALANCE_HISTORY + currency
        return self._get_method(api_path=url,
                                         func_description="company balance list by user",
                                         logger=logger,
                                         is_getting_list= True)


    def _add_company_balance(self, currency, body):
        url = settings.COMPANY_BALANCE_ADD + currency
        data, success = self._post_method(api_path=url,
                                          func_description="company balance by user",
                                          logger= logger, 
                                          params=body)
        return success

    def _get_currency_choices_by_agent(self,agent_id):
        url = settings.GET_AGET_BALANCE.format(agent_id)
        data, success = self._get_method(api_path=url,
                                        func_description="currency list by agent",
                                        logger=logger,
                                        is_getting_list=True)
        if success:
            currency_list = [i['currency'] for i in data]
            return currency_list, True
        else:
            return [], True
        

company_balance = login_required(CompanyBalanceView.as_view(), login_url='login')
