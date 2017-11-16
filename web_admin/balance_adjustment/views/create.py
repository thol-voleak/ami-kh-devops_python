from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
import ast
from django.views.generic.base import TemplateView
from django.shortcuts import render, redirect
from braces.views import GroupRequiredMixin
from authentications.apps import InvalidAccessToken
from web_admin import api_settings, setup_logger, RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin
from django.contrib import messages
import logging
from web_admin.api_logger import API_Logger

logger = logging.getLogger(__name__)

class BalanceAdjustmentCreateView(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    group_required = "SYS_BAL_ADJUST_REQUEST"
    login_url = 'web:permission_denied'
    raise_exception = False

    template_name = "balance_adjustment/create.html"
    path = api_settings.ORDER_BAL_ADJUST_PATH
    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(BalanceAdjustmentCreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(BalanceAdjustmentCreateView, self).get_context_data(**kwargs)
        services = self.get_services_list()
        self.update_step_to_service(services)
        context.update({'services': services})
        context.update({'currency': self.get_currency_list().get('value')})
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = super(BalanceAdjustmentCreateView, self).get_context_data(**kwargs)
        self.logger.info('========== Start create order balance adjustment ==========')
        agent_id = request.POST.get('agent_id')
        initiator_source_of_fund_id = request.POST.get('initiator_source_of_fund_id')
        ref_order_id = request.POST.get('ref_order_id')
        reason = request.POST.get('reason_for_adjustment')
        payer_id = request.POST.get('payer_id')
        payer_type = request.POST.get('payer_type')
        payer_source_of_fund_id = request.POST.get('payer_source_of_fund_id')
        payee_id = request.POST.get('payee_id')
        payee_type = request.POST.get('payee_type')
        payee_source_of_fund_id = request.POST.get('payee_source_of_fund_id')
        amountstr = request.POST.get('amount')
        if isinstance(amountstr, str):
            amountstr = amountstr.replace(',', '')
        amount = float(amountstr)
        service = request.POST.get('service_name')
        service = ast.literal_eval(service)
        service_name = service['service_name']
        service_id = service['service_id']
        user_type = {'customer': 1, 'agent': 2}

        params = {
            "product_service_id": service_id,
            "reference_order_id": ref_order_id,
            "reason": reason,
            "initiator": {
                "user_id": agent_id,
                "user_type": {
                    'id': 2,   # always be agent
                },
                "sof": {
                    "id": initiator_source_of_fund_id,
                    "type_id": 2                    # always be cash
                }
            },
            "payer_user": {
                "user_id": payer_id,
                "user_type": {
                    'id': user_type[payer_type]
                },
                "sof": {
                    "id": payer_source_of_fund_id,
                    "type_id": 2                    # always be cash
                }
            },
            "payee_user": {
                "user_id": payee_id,
                "user_type": {
                    'id': user_type[payee_type]
                },
                "sof": {
                    "id": payee_source_of_fund_id,
                    "type_id": 2                    # always be cash
                }
            },
            "amount": amount
        }

        success, status_code, message, data = RestFulClient.post(
            url=self.path,
            headers=self._get_headers(),
            loggers=self.logger,
            params=params)

        API_Logger.post_logging(loggers=self.logger, params=params, response=data, status_code=status_code)
        self.logger.info('========== Finish create order balance adjustment ==========')
        if success:
            messages.success(request, 'The adjustment is created successfully')
            return redirect('balance_adjustment:balance_adjustment_list')
        else:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format(message))
                raise InvalidAccessToken(message)

            context = {
                'agent_id': agent_id,
                'initiator_source_of_fund_id': initiator_source_of_fund_id,
                'ref_order_id': ref_order_id,
                'reason_for_adjustment': reason,
                'payer_id': payer_id,
                'payer_type': payer_type,
                'payer_source_of_fund_id': payer_source_of_fund_id,
                'payee_id': payee_id,
                'payee_type': payee_type,
                'payee_source_of_fund_id': payee_source_of_fund_id,
                'amount': request.POST.get('amount'),
                'service_name': service_name,
                'currency': self.get_currency_list().get('value'),
            }

            services = self.get_services_list()
            self.update_step_to_service(services)
            context.update({'services': services})

            if status_code.lower() in ["general_error"]:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Other error, please contact system administrator"
                )
            elif message == 'timeout':
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Request timed-out, please try again or contact system administrator"
                )
            else:
                messages.add_message (
                    request,
                    messages.ERROR,
                    message
                )

            return render(request, self.template_name, context) #

    def get_services_list(self):
        url = api_settings.SERVICE_LIST_URL
        success, status_code, data  = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        if not success:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format('access_token_expire'))
                raise InvalidAccessToken('access_token_expire')
        return data

    def get_currency_list(self):
        url = api_settings.GET_ALL_CURRENCY_URL
        success, status_code, data  = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        if not success:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format('access_token_expire'))
                raise InvalidAccessToken('access_token_expire')
        return data

    def update_step_to_service(self, services):
        currencies = self.get_currency_list().get('value')
        for service in services:
            currency = service['currency']
            decimal = int(currencies.split(currency + '|')[1].split(',')[0])
            if decimal == 1:
                step = '0.1'
            elif decimal > 1:
                step = '0.' + '0'*(decimal-1) + '1'
            else:
                step = '1'
            service['step'] = step