from braces.views import GroupRequiredMixin

from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger
from web_admin.api_settings import PAYMENT_URL, SERVICE_LIST_URL
from web_admin.restful_methods import RESTfulMethods

from django.shortcuts import render
from django.views.generic.base import TemplateView
import logging
from datetime import datetime
logger = logging.getLogger(__name__)

IS_SUCCESS = {
    True: 'Success',
    False: 'Failed',
}

STATUS_ORDER = {
    -1: 'FAIL',
     0: 'CREATED',
     1: 'LOCKING',
     2: 'EXECUTED',
     3: 'ROLLED_BACK',
     4: 'TIME_OUT',
}

class PaymentOrderView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    template_name = "payments/payment_order.html"
    logger = logger

    group_required = "CAN_SEARCH_PAYMENT_ORDER"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(PaymentOrderView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start render payment order ==========')
        context = super(PaymentOrderView, self).get_context_data(**kwargs)
        data = self.get_services_list()
        status_list = [
            {"id": -1, "name": "FAIL"},
            {"id": 0, "name": "CREATED"},
            {"id": 1, "name": "LOCKING"},
            {"id": 2, "name": "EXECUTED"},
            {"id": 3, "name": "ROLLED_BACK"},
            {"id": 4, "name": "TIME_OUT"},
        ]

        context['data'] = data
        context['search_count'] = 0
        context['status_list'] = status_list
        context['status_id'] = ''

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start searching payment order ==========')

        order_id = request.POST.get('order_id')
        service_name = request.POST.get('service_name')
        payer_user_id = request.POST.get('payer_user_id')
        payer_user_type_id = request.POST.get('payer_user_type_id')
        payee_user_id = request.POST.get('payee_user_id')
        payee_user_type_id = request.POST.get('payee_user_type_id')
        from_created_timestamp = request.POST.get('from_created_timestamp')
        to_created_timestamp = request.POST.get('to_created_timestamp')
        service_list = self.get_services_list()
        ext_transaction_id = request.POST.get('ext_transaction_id')
        status_id = request.POST.get('status_id')
        creation_client_id = request.POST.get('creation_client_id')
        execution_client_id = request.POST.get('execution_client_id')

        body = {}
        if order_id:
            body['order_id'] = order_id
        if service_name:
            body['service_name'] = service_name
        if payer_user_id:
            body['payer_user_id'] = payer_user_id
        if payer_user_type_id.isdigit() and payer_user_type_id != '0':
            body['payer_user_type_id'] = int(payer_user_type_id)
        if payee_user_id:
            body['payee_user_id'] = payee_user_id
        if payee_user_type_id.isdigit() and payee_user_type_id != '0':
            body['payee_user_type_id'] = int(payee_user_type_id)

        if ext_transaction_id:
            body['ext_transaction_id'] = ext_transaction_id
        if status_id:
            body['status_id'] = [int(status_id)]

        if creation_client_id:
            body['created_client_id'] = creation_client_id
        if execution_client_id:
            body['executed_client_id'] = execution_client_id

        if from_created_timestamp is not '' and to_created_timestamp is not None:
            new_from_created_timestamp = datetime.strptime(from_created_timestamp, "%Y-%m-%d")
            new_from_created_timestamp = new_from_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['from'] = new_from_created_timestamp

        if to_created_timestamp is not '' and to_created_timestamp is not None:
            new_to_created_timestamp = datetime.strptime(to_created_timestamp, "%Y-%m-%d")
            new_to_created_timestamp = new_to_created_timestamp.replace(hour=23, minute=59, second=59)
            new_to_created_timestamp = new_to_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['to'] = new_to_created_timestamp

        data, status = self.get_payment_order_list(body=body)
        for i in data:
            if i['currency'] == 'VND':
                i['amount'] = int(i['amount'])

        if data:
            result_data = self.format_data(data)
        else:
            result_data = data

        order_list = self.refine_data(result_data)
        count = 0
        if len(order_list):
            count = len(order_list)

        status_list = [
            {"id": -1, "name": "FAIL"},
            {"id": 0, "name": "CREATED"},
            {"id": 1, "name": "LOCKING"},
            {"id": 2, "name": "EXECUTED"},
            {"id": 3, "name": "ROLLED_BACK"},
            {"id": 4, "name": "TIME_OUT"},
        ]

        context = {'order_list': order_list,
                   'order_id': order_id,
                   'service_name': service_name,
                   'data': service_list,
                   'payer_user_id': payer_user_id,
                   'payer_user_type_id':payer_user_type_id,
                   'payee_user_id': payee_user_id,
                   'payee_user_type_id':payee_user_type_id,
                   'search_count': count,
                   'creation_client_id': creation_client_id,
                   'execution_client_id': execution_client_id,
                   'ext_transaction_id': ext_transaction_id,
                   'status_list': status_list,
                   'date_from': from_created_timestamp,
                   'date_to': to_created_timestamp,
                   }

        if status_id:
            context['status_id'] = int(status_id)

        self.logger.info('========== Finished searching payment order ==========')

        return render(request, self.template_name, context)

    def get_payment_order_list(self, body):
        response, status = self._post_method(PAYMENT_URL, 'Payment Order List', logger, body)
        return response, status

    def format_data(self, data):
        for i in data:
            i['is_stopped'] = IS_SUCCESS.get(i.get('is_stopped'))
        return data

    def refine_data(self, data):
        for item in data:
            item['status'] = STATUS_ORDER.get(item['status'], 'UN_KNOWN')
        return data


    def get_services_list(self):
        url = SERVICE_LIST_URL
        data, success = self._get_method(api_path=url, func_description="service list", is_getting_list=True)
        return data
        