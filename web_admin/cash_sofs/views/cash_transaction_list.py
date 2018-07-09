from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.api_settings import CASH_TRANSACTIONS_URL
from web_admin.restful_methods import RESTfulMethods
from web_admin.api_logger import API_Logger
from django.shortcuts import render
from django.views.generic.base import TemplateView
from datetime import date, timedelta
from braces.views import GroupRequiredMixin
from web_admin import api_settings, setup_logger, RestFulClient
from web_admin.utils import calculate_page_range_from_page_info, convert_string_to_date_time
import logging

logger = logging.getLogger(__name__)

IS_SUCCESS = {
    True: 'Success',
    False: 'Failed',
}


class CashTransactionView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_SEARCH_CASH_TXN"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "cash_transaction.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CashTransactionView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = {"search_count": 0}
        self.initSearchDateTime(context)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start search cash transaction ==========')

        user_id = request.POST.get('user_id')
        user_type_id = request.POST.get('user_type_id')
        sof_id = request.POST.get('sof_id')
        order_id = request.POST.get('order_id')
        order_detail_id = request.POST.get('order_detail_id')
        action_id = request.POST.get('action_id')
        status_id = request.POST.get('status_id')
        opening_page_index = request.POST.get('current_page_index')

        created_from_date = request.POST.get('created_from_date')
        created_to_date = request.POST.get('created_to_date')
        created_from_time = request.POST.get('created_from_time')
        created_to_time = request.POST.get('created_to_time')
        modified_from_date = request.POST.get('modified_from_date')
        modified_to_date = request.POST.get('modified_to_date')
        modified_from_time = request.POST.get('modified_from_time')
        modified_to_time = request.POST.get('modified_to_time')

        body = {'paging': True, 'page_index': int(opening_page_index)}
        if user_id is not '':
            body['user_id'] = int(user_id)
        if user_type_id is not '' and user_type_id is not '0':
            body['user_type_id'] = int(0 if user_type_id is None else user_type_id)
        if sof_id is not '':
            body['sof_id'] = int(sof_id)
        if order_id is not '':
            body['order_id'] = order_id
        if order_detail_id is not '':
            body['order_detail_id'] = order_detail_id
        if action_id is not '':
            body['action_id'] = int(action_id)
        if status_id is not '':
            body['status_id'] = int(status_id)
        if created_from_date:
            body['from_created_timestamp'] = convert_string_to_date_time(created_from_date, created_from_time)
        if created_to_date:
            body['to_created_timestamp'] = convert_string_to_date_time(created_to_date, created_to_time)
        if modified_from_date:
            body['from_last_updated_timestamp'] = convert_string_to_date_time(modified_from_date, modified_from_time)
        if modified_to_date:
            body['to_last_updated_timestamp'] = convert_string_to_date_time(modified_to_date, modified_to_time)

        context = {}
        data, success, status_message = self.get_cash_transaction_list(body)
        if success:
            cards_list = data.get("cash_sof_transactions", [])
            cards_list = self.format_data(cards_list)
            page = data.get("page", {})
            self.logger.info("Page: {}".format(page))

            context.update({
                'search_count': page.get('total_elements', 0),
                'paginator': page,
                'page_range': calculate_page_range_from_page_info(page),
                'transaction_list': cards_list
            })
        else:
            context.update({
                'search_count': 0,
                'paginator': {},
                'transaction_list': []
            })

        context.update({
            'user_id': user_id,
            'user_type_id': user_type_id,
            'search_by': body,
            'sof_id': sof_id,
            'order_id': order_id,
            'order_detail_id': order_detail_id,
            'action_id': action_id,
            'status_id': status_id,
            'created_from_date': created_from_date,
            'created_to_date': created_to_date,
            'created_from_time': created_from_time,
            'created_to_time': created_to_time,
            'modified_from_date': modified_from_date,
            'modified_to_date': modified_to_date,
            'modified_from_time': modified_from_time,
            'modified_to_time': modified_to_time
        })

        self.logger.info('========== End search cash transaction ==========')
        return render(request, self.template_name, context)

    def get_cash_transaction_list(self, body):
        success, status_code, status_message, data = RestFulClient.post(url=CASH_TRANSACTIONS_URL,
                                                                        headers=self._get_headers(),
                                                                        loggers=self.logger,
                                                                        params=body)
        data = data or {}
        API_Logger.post_logging(loggers=self.logger, params=body, response=data.get('cash_sof_transactions', []),
                                status_code=status_code, is_getting_list=True)
        return data, success, status_message

    def format_data(self, data):
        for i in data:
            i['is_success'] = IS_SUCCESS.get(i.get('is_success'))
        return data

    def initSearchDateTime(self, context):
        today = date.today()
        yesterday = today - timedelta(1)
        tomorrow = today + timedelta(1)
        context['created_from_date'] = yesterday.strftime('%Y-%m-%d')
        context['created_to_date'] = tomorrow.strftime('%Y-%m-%d')
        context['created_from_time'] = "00:00:00"
        context['created_to_time'] = "00:00:00"
        context['modified_from_date'] = yesterday.strftime('%Y-%m-%d')
        context['modified_to_date'] = tomorrow.strftime('%Y-%m-%d')
        context['modified_from_time'] = "00:00:00"
        context['modified_to_time'] = "00:00:00"
