from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
import ast
from django.views.generic.base import TemplateView
from django.shortcuts import render, redirect
from braces.views import GroupRequiredMixin
from django.contrib import messages
from authentications.apps import InvalidAccessToken
from web_admin import api_settings, setup_logger, RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin
from django.contrib import messages
import logging

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
        context.update({'services': services})
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = super(BalanceAdjustmentCreateView, self).get_context_data(**kwargs)
        self.logger.info('========== Start create order balance adjustment ==========')
        agent_id = request.POST.get('agent_id')
        initiator_source_of_fund_id = request.POST.get('initiator_source_of_fund_id')
        product_name = request.POST.get('product_name')
        product_reference_1 = request.POST.get('product_reference_1')
        product_reference_2 = request.POST.get('product_reference_2')
        product_reference_3 = request.POST.get('product_reference_3')
        payer_id = request.POST.get('payer_id')
        payer_type = request.POST.get('payer_type')
        payer_source_of_fund_id = request.POST.get('payer_source_of_fund_id')
        payee_id = request.POST.get('payee_id')
        payee_type = request.POST.get('payee_type')
        payee_source_of_fund_id = request.POST.get('payee_source_of_fund_id')
        amount = float(request.POST.get('amount'))
        service = request.POST.get('service_name')
        service = ast.literal_eval(service)
        service_name = service['service_name']
        service_id = service['service_id']
        currency = service['currency']

        params = {
            "initiator": {
                "user_id": agent_id,
                "user_type": "agent",
                "ref": None,
                "sof": {
                    "id": initiator_source_of_fund_id,
                    "type_id": 2,
                    "currency":""
                }
            },
            "order_create_request": {
                "ext_transaction_id": "",
                "product_service": {
                    "id": service_id,
                    "name": service_name,
                    "currency": currency
                },
                "product": {
                    "product_name": product_name,
                    "product_ref1": product_reference_1,
                    "product_ref2": product_reference_2,
                    "product_ref3": product_reference_3,
                    "product_ref4": "Ref4",
                    "product_ref5": "Ref5"
                },
                "payer_user": {
                    "user_id": payer_id,
                    "user_type": payer_type,
                    "ref": None,
                    "sof": {
                        "id": payer_source_of_fund_id,
                        "type_id": 2,
                        "currency":""
                    }
                },
                "payee_user": {
                    "user_id": payee_id,
                    "user_type": payee_type,
                    "ref": None,
                    "sof": {
                        "id": payee_source_of_fund_id,
                        "type_id": 2,
                        "currency":""
                    }
                },
                "amount": amount
            }
        }

        self.logger.info('Params: {}'.format(params))

        success, status_code, message, data = RestFulClient.post(
            url=self.path,
            headers=self._get_headers(),
            loggers=self.logger,
            params=params)

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
                'product_reference_1': product_reference_1,
                'product_reference_2': product_reference_2,
                'product_reference_3': product_reference_3,
                'payer_id': payer_id,
                'payer_type': payer_type,
                'payer_source_of_fund_id': payer_source_of_fund_id,
                'payee_id': payee_id,
                'payee_type': payee_type,
                'payee_source_of_fund_id': payee_source_of_fund_id,
                'amount': request.POST.get('amount'),
                'service_name': service_name,
                'product_name': product_name,
            }

            services = self.get_services_list()
            context.update({'services': services})

            if status_code.lower() in ["payment_not_allow"]:
                messages.add_message(
                    request,
                    messages.ERROR,
                    message
                )
            else:
                messages.add_message (
                    request,
                    messages.ERROR,
                    "Other error, please contact system administrator"
                )

            return render(request, self.template_name, context)

    def get_services_list(self):
        url = api_settings.SERVICE_LIST_URL
        success, status_code, data  = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        if not success:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format('access_token_expire'))
                raise InvalidAccessToken('access_token_expire')
        return data