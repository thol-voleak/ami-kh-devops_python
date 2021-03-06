import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView

from web_admin.exceptions import PermissionDeniedException
from web_admin.mixins import GetChoicesMixin
from web_admin.restful_methods import RESTfulMethods
from web_admin.api_settings import GET_REPORT_AGENT_BALANCE
from web_admin.api_settings import COMPANY_BALANCE_HISTORY
from web_admin.api_settings import COMPANY_BALANCE_ADD
from web_admin.api_settings import GET_AGENT_BALANCE
from web_admin import api_settings, setup_logger
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from braces.views import GroupRequiredMixin

logger = logging.getLogger(__name__)


class CompanyBalanceView(GroupRequiredMixin, TemplateView, GetChoicesMixin, RESTfulMethods):
    group_required = "SYS_VIEW_COMPANY_BALANCE"
    login_url = 'web:permission_denied'
    raise_exception = False

    template_name = "company_balance.html"
    company_agent_id = 1
    company_agent_user_type = 2
    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CompanyBalanceView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name,
                      self._build_context(request)
                      )

    def post(self, request, *args, **kwargs):
        if not check_permissions_by_user(request.user, 'SYS_ADD_COMPANY_BALANCE'):
            raise PermissionDeniedException()

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

    def _get_company_balance(self, currency):
        url = GET_REPORT_AGENT_BALANCE
        body = {
            'user_id': self.company_agent_id,
            'currency': currency,
            'user_type': 2,
            "paging": False,
            "page_index": -1
        }
        func_description = "Getting balance by username: {} \
        ,agent id: {} and currency: {}".format(self.request.user.username,
                                               self.company_agent_id,
                                               currency, )
        return self._post_method(api_path=url,
                                 func_description=func_description,
                                 logger=logger,
                                 params=body)

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
        return self._put_method(api_path=url,
                                func_description="add company balance",
                                logger=logger,
                                params=body)

    def _get_currency_choices_by_agent(self, agent_id, company_agent_user_type):
        url = GET_AGENT_BALANCE
        body = {'user_id': agent_id, 'user_type': company_agent_user_type, 'paging':False}
        data, success = self._post_method(api_path=url,
                                          func_description="currency list by agent",
                                          logger=logger,
                                          params=body)
        if success:
            currency_list = [i['currency'] for i in data['cash_sofs']]
            return currency_list, True
        else:
            return data, True

    def _get_currency_choices_list(self):
        url = api_settings.GET_ALL_CURRENCY_URL
        self.logger.info('Get currency choice list from backend')
        data, success = self._get_method(api_path=url,
                                         func_description="currency choice list",
                                         logger=logger,
                                         is_getting_list=False)
        if success:
            value = data.get('value', '')
            if isinstance(value, str):
                currency_list = map(lambda x: x.split('|'), value.split(','))
            else:
                currency_list = []
            result = currency_list, True
        else:
            result = data, False
        return result

    def sum_balance(self, balance_lst):
        return sum([balance['changed_amount'] for balance in balance_lst])

    def _build_context(self, request):
        default_decimal = 1
        currency_choices, success_currency = self._get_currency_choices_by_agent(self.company_agent_id,
                                                                                 self.company_agent_user_type)
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
            return {'objects': [],
                    'currency_list': [],
                    'decimal': None,
                    'company_balance': None,
                    'total_balance': None}

        totalData, success_total_balance = self._get_company_balance(currency)

        if not success_total_balance:
            messages.add_message(
                request,
                messages.ERROR,
                message=totalData
            )
            totalData = {}
        else:
            totalData = totalData['cash_sofs'][0]

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
        objs = list(data)
        return {
            'objects': objs,
            'currency_list': currency_list,
            'decimal': decimal,
            'company_balance': totalData,
            'total_balance': self.sum_balance(objs)
        }


company_balance = login_required(CompanyBalanceView.as_view(), login_url='authentications:login')
