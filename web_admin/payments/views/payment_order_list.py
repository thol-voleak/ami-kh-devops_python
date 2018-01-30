from braces.views import GroupRequiredMixin
from web_admin.utils import calculate_page_range_from_page_info
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger
from web_admin.api_settings import PAYMENT_URL, SERVICE_LIST_URL
from web_admin.restful_methods import RESTfulMethods
from web_admin.restful_client import RestFulClient
from web_admin.api_logger import API_Logger
from django.shortcuts import render
from authentications.apps import InvalidAccessToken
from django.views.generic.base import TemplateView
import logging
from django.contrib import messages
from datetime import datetime
logger = logging.getLogger(__name__)

IS_SUCCESS = {
    True: 'Success',
    False: 'Failed',
}

STATUS_ORDER = {
    -1: 'Fail',
     0: 'Created',
     1: 'Locking',
     2: 'Executed',
     3: 'Rolled back',
     4: 'Time out',
}

class PaymentOrderView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    template_name = "payments/payment_order.html"
    logger = logger

    group_required = "CAN_MANAGE_PAYMENT"
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
            {"id": 0, "name": "Created"},
            {"id": 2, "name": "Executed"},
            {"id": -1, "name": "Fail"},
            {"id": 1, "name": "Locking"},
            {"id": 3, "name": "Rolled back"},
            {"id": 4, "name": "Time out"},
        ]
        error_list = [
            {"name": "All", "title": "All"},
            {"name": "insufficient_fund", "title": "Insufficient Fund"},
            {"name": "security_code_expired", "title": "Security Code Expired"},
            {"name": "security_code_failed", "title": "Security Code Failed"},
            {"name": "invalid_request", "title": "Invalid Request"},
            {"name": "payment_not_allow", "title": "Payment Not Allow"},
            {"name": "cancel_order_not_allow", "title": "Cancel Order Not Allow"},
            {"name": "general_error", "title": "General Error"},
            {"name": "internal_error", "title": "Internal Error"},
            {"name": "internal_server_error", "title": "Internal Server Error"},
            {"name": "internal_call_timeout", "title": "Internal Call Timeout"},
            {"name": "bad_request", "title": "Bad Request"},
        ]

        error_code_id = []
        status_code_id = []

        context['data'] = data
        context['search_count'] = 0
        context['status_list'] = status_list
        context['error_list'] = error_list
        context['error_code_id'] = error_code_id
        context['status_code_id'] = status_code_id
        context['permissions'] = self._get_has_permissions()
        self.logger.info('========== Finish render payment order ==========')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start searching payment order ==========')

        order_id = request.POST.get('order_id')
        service_name = request.POST.get('service_name')
        user_id = request.POST.get('user_id')
        user_type_id = request.POST.get('user_type')
        from_created_timestamp = request.POST.get('from_created_timestamp')
        to_created_timestamp = request.POST.get('to_created_timestamp')
        self.logger.info('========== Start getting service list ==========')
        service_list = self.get_services_list()
        self.logger.info('========== Finish getting service list ==========')
        ext_transaction_id = request.POST.get('ext_transaction_id')
        list_status_id = request.POST.getlist('list_status_id')
        creation_client_id = request.POST.get('creation_client_id')
        execution_client_id = request.POST.get('execution_client_id')
        opening_page_index = request.POST.get('current_page_index')
        error_code = request.POST.getlist('error_code_id')
        error_code_search = error_code

        if 'All' in error_code:
            error_code_search = ["insufficient_fund", "security_code_expired","security_code_failed","invalid_request",
                          "payment_not_allow", "cancel_order_not_allow", "general_error"]
            error_code = ["All"]

        list_status_search = []
        for status in list_status_id:
            list_status_search.append(int(status))
        list_status_id = list(list_status_search)

        body = {}
        body['paging'] = True
        body['page_index'] = int(opening_page_index)
        if order_id:
            body['order_id'] = order_id
        if service_name:
            body['service_name'] = service_name
        if user_id and user_id.isdigit():
            body['user_id'] = int(user_id)
        elif user_id:
            body['user_id'] = user_id
        if user_type_id.isdigit() and user_type_id != '0':
            body['user_type_id'] = int(user_type_id)
        if ext_transaction_id:
            body['ext_transaction_id'] = ext_transaction_id

        if list_status_search:
            body['status_id_list'] = list_status_search

        if creation_client_id:
            body['created_client_id'] = creation_client_id
        if execution_client_id:
            body['executed_client_id'] = execution_client_id
        if error_code_search:
            body['error_code'] = error_code_search

        if from_created_timestamp is not '' and to_created_timestamp is not None:
            new_from_created_timestamp = datetime.strptime(from_created_timestamp, "%Y-%m-%d")
            new_from_created_timestamp = new_from_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['from'] = new_from_created_timestamp

        if to_created_timestamp is not '' and to_created_timestamp is not None:
            new_to_created_timestamp = datetime.strptime(to_created_timestamp, "%Y-%m-%d")
            new_to_created_timestamp = new_to_created_timestamp.replace(hour=23, minute=59, second=59)
            new_to_created_timestamp = new_to_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['to'] = new_to_created_timestamp

        data = self.get_payment_order_list(body=body)

        if data:
            result_data = self.format_data(data)
        else:
            result_data = data

        order_list = self.refine_data(result_data)
        orders = order_list.get("orders", [])
        page = order_list.get("page", {})
        self.logger.info('Page : {}'.format(page))
        count = 0
        if len(order_list):
            count = len(order_list)

        status_list = [
            {"id": 0, "name": "Created"},
            {"id": 2, "name": "Executed"},
            {"id": -1, "name": "Fail"},
            {"id": 1, "name": "Locking"},
            {"id": 3, "name": "Rolled back"},
            {"id": 4, "name": "Time out"},
        ]

        error_list = [
            {"name": "All", "title": "All"},
            {"name": "insufficient_fund", "title": "Insufficient Fund"},
            {"name": "security_code_expired", "title": "Security Code Expired"},
            {"name": "security_code_failed", "title": "Security Code Failed"},
            {"name": "invalid_request", "title": "Invalid Request"},
            {"name": "payment_not_allow", "title": "Payment Not Allow"},
            {"name": "cancel_order_not_allow", "title": "Cancel Order Not Allow"},
            {"name": "general_error", "title": "General Error"},
            {"name": "internal_error", "title": "Internal Error"},
            {"name": "internal_server_error", "title": "Internal Server Error"},
            {"name": "internal_call_timeout", "title": "Internal Call Timeout"},
            {"name": "bad_request", "title": "Bad Request"},
        ]

        context = {'order_list': orders,
                   'order_id': order_id,
                   'service_name': service_name,
                   'data': service_list,
                   'user_type':user_type_id,
                   'user_id': user_id,
                   'search_count': page.get('total_elements', 0),
                   'creation_client_id': creation_client_id,
                   'execution_client_id': execution_client_id,
                   'ext_transaction_id': ext_transaction_id,
                   'status_list': status_list,
                   'error_list': error_list,
                   'date_from': from_created_timestamp,
                   'date_to': to_created_timestamp,
                   'permissions': self._get_has_permissions(),
                   'paginator': page,
                   'page_range': calculate_page_range_from_page_info(page),
        }

        if list_status_id:
            context['status_code_id'] = list_status_id
        if error_code:
            context['error_code_id'] = error_code

        self.logger.info('========== Finished searching payment order ==========')

        return render(request, self.template_name, context)

    def get_payment_order_list(self, body):
        is_success, status_code, status_message, data = RestFulClient.post(url=PAYMENT_URL,
                                                                           headers=self._get_headers(), 
                                                                           loggers=self.logger, 
                                                                           params=body)

        API_Logger.post_logging(loggers=self.logger, params=body, response=data['orders'],
                                status_code=status_code, is_getting_list=True)

        if not is_success:
            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )
            data = []
        return data

    def format_data(self, data):
        for i in data['orders']:
            i['is_stopped'] = IS_SUCCESS.get(i.get('is_stopped'))
        return data

    def refine_data(self, data):
        for item in data['orders']:
            item['status'] = STATUS_ORDER.get(item['status'], 'UN_KNOWN')
        return data

    def get_services_list(self):
        url = SERVICE_LIST_URL
        success, status_code, data  = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        if not success:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format('access_token_expire'))
                raise InvalidAccessToken('access_token_expire')
        return data

    def _get_has_permissions(self):
        permissions = {
            'is_perm_order_detail': check_permissions_by_user(self.request.user, "CAN_VIEW_PAYMENT_ORDER_DETAIL"),
            'is_perm_order_search': check_permissions_by_user(self.request.user, "CAN_SEARCH_PAYMENT_ORDER"),
        }
        return permissions