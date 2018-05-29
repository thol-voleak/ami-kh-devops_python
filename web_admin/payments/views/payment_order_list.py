from braces.views import GroupRequiredMixin
from web_admin.utils import calculate_page_range_from_page_info, make_download_file, export_file
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger
from web_admin.api_settings import PAYMENT_URL, SERVICE_LIST_URL
from web_admin.restful_methods import RESTfulMethods
from web_admin.restful_client import RestFulClient
from web_admin.api_logger import API_Logger
from django.shortcuts import render
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
        services = self.get_services_list()
        services.sort(key = lambda service: service['service_name'])
        request.session['page_from'] = 'order_list'

        error_code_id = []
        status_code_id = []

        context['services'] = services
        context['search_count'] = 0
        context['status_list'] = status_list
        context['error_list'] = error_list
        context['error_code_id'] = error_code_id
        context['status_code_id'] = status_code_id
        context['permissions'] = self._get_has_permissions()
        context['is_show_export'] = False
        self.logger.info('========== Finish render payment order ==========')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        order_id = request.POST.get('order_id')
        searched_services = request.POST.getlist('service_name')
        user_id = request.POST.get('user_id')
        user_type_id = request.POST.get('user_type')
        from_created_timestamp = request.POST.get('from_created_timestamp')
        to_created_timestamp = request.POST.get('to_created_timestamp')
        ext_transaction_id = request.POST.get('ext_transaction_id')
        list_status_id = request.POST.getlist('list_status_id')
        product_name = request.POST.get('product_name')
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
        if order_id:
            body['order_id'] = order_id
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

        if product_name:
            body['product_name'] = product_name
        if creation_client_id:
            body['created_client_id'] = creation_client_id
        if execution_client_id:
            body['executed_client_id'] = execution_client_id
        if error_code_search:
            body['error_codes'] = error_code_search
        if searched_services:
            searched_services = [int(i) for i in searched_services if i.isnumeric()]
            body['service_id_list'] = searched_services

        if from_created_timestamp is not '' and to_created_timestamp is not None:
            new_from_created_timestamp = datetime.strptime(from_created_timestamp, "%Y-%m-%d")
            new_from_created_timestamp = new_from_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['from'] = new_from_created_timestamp

        if to_created_timestamp is not '' and to_created_timestamp is not None:
            new_to_created_timestamp = datetime.strptime(to_created_timestamp, "%Y-%m-%d")
            new_to_created_timestamp = new_to_created_timestamp.replace(hour=23, minute=59, second=59)
            new_to_created_timestamp = new_to_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['to'] = new_to_created_timestamp

        if 'download' in request.POST:
            self.logger.info('========== Start exporting payment order ==========')
            file_type = request.POST.get('export-type')
            body['file_type'] = file_type
            body['row_number'] = 5000
            is_success, data = export_file(self, body=body, url_download=PAYMENT_URL, api_logger=API_Logger)
            if is_success:
                response = make_download_file(data, file_type)
                self.logger.info('========== Finish exporting payment order ==========')
                return response

        if 'search' in request.POST:
            self.logger.info('========== Start getting service list ==========')
            services = self.get_services_list()
            services.sort(key=lambda service: service['service_name'])
            self.logger.info('========== Finish getting service list ==========')
            self.logger.info('========== Start searching payment order ==========')
            body['paging'] = True
            body['page_index'] = int(opening_page_index)
            data, is_success = self.get_payment_order_list(body=body)

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

            context = {'order_list': orders,
                       'order_id': order_id,
                       'searched_services': searched_services,
                       'services': services,
                       'user_type':user_type_id,
                       'user_id': user_id,
                       'search_count': page.get('total_elements', 0),
                       'product_name': product_name,
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

            if is_success:
                context['is_show_export'] = True
            else:
                context['is_show_export'] = False

            if list_status_id:
                context['status_code_id'] = list_status_id
            if error_code:
                context['error_code_id'] = error_code

            self.logger.info('========== Finished searching payment order ==========')

            return render(request, self.template_name, context)

    def get_payment_order_list(self, body):
        # url = 'http://localhost:1236/search_order'
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
        return data, is_success

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
        API_Logger.get_logging(loggers=self.logger,
                               response=data,
                               status_code=status_code)
        return data

    def _get_has_permissions(self):
        permissions = {
            'is_perm_order_detail': check_permissions_by_user(self.request.user, "CAN_VIEW_PAYMENT_ORDER_DETAIL"),
            'is_perm_order_search': check_permissions_by_user(self.request.user, "CAN_SEARCH_PAYMENT_ORDER"),
        }
        return permissions