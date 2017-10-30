from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.api_settings import CASH_TRANSACTIONS_URL
from web_admin.restful_methods import RESTfulMethods
from web_admin.api_logger import API_Logger
from django.shortcuts import render
from django.views.generic.base import TemplateView
from datetime import datetime
from braces.views import GroupRequiredMixin
from web_admin import api_settings, setup_logger, RestFulClient
from web_admin.utils import calculate_page_range_from_page_info
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
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start search cash transaction ==========')

        sof_id = request.POST.get('sof_id')
        order_id = request.POST.get('order_id')
        action_id = request.POST.get('action_id')
        status_id = request.POST.get('status_id')
        opening_page_index = request.POST.get('current_page_index')

        from_created_timestamp = request.POST.get('from_created_timestamp')
        to_created_timestamp = request.POST.get('to_created_timestamp')

        body = {}
        body['paging'] = True
        body['page_index'] = int(opening_page_index)
        if sof_id is not '':
            body['sof_id'] = int(sof_id)
        if order_id is not '':
            body['order_id'] = order_id
        if action_id is not '':
            body['action_id'] = int(action_id)
        if status_id is not '':
            body['status_id'] = int(status_id)
        if from_created_timestamp is not '' and to_created_timestamp is not None:
            new_from_created_timestamp = datetime.strptime(from_created_timestamp, "%Y-%m-%d")
            new_from_created_timestamp = new_from_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['from_created_timestamp'] = new_from_created_timestamp
            self.logger.info("from_created_timestamp [{}]".format(new_from_created_timestamp))
        if to_created_timestamp is not '' and to_created_timestamp is not None:
            new_to_created_timestamp = datetime.strptime(to_created_timestamp, "%Y-%m-%d")
            new_to_created_timestamp = new_to_created_timestamp.replace(hour=23, minute=59, second=59)
            new_to_created_timestamp = new_to_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['to_created_timestamp'] = new_to_created_timestamp
            self.logger.info("to_created_timestamp [{}]".format(new_to_created_timestamp))

        self.logger.info("keyword for search is [{}]".format(body))

        context = {}
        data, success, status_message = self.get_cash_transaction_list(body)
        body['from_created_timestamp'] = from_created_timestamp
        body['to_created_timestamp'] = to_created_timestamp
        if success:
            cards_list = data.get("cash_sof_transactions", [])
            cards_list = self.format_data(cards_list)
            page = data.get("page", {})
            context.update(
                {'search_count': page.get('total_elements', 0),
                 'paginator': page,
                 'page_range': calculate_page_range_from_page_info(page),
                 # 'user_id': user_id,
                 'search_by': body,
                 'transaction_list': cards_list,
                 'sof_id': sof_id,
                 'order_id': order_id,
                 'action_id': action_id,
                 'status_id': status_id,
                 'from_created_timestamp': from_created_timestamp,
                 'to_created_timestamp': to_created_timestamp
                 }
            )
        else:
            context.update(
                {'search_count': 0,
                 'paginator': {},
                 # 'user_id': user_id,
                 'search_by': body,
                 'transaction_list': [],
                 'sof_id': sof_id,
                 'order_id': order_id,
                 'action_id': action_id,
                 'status_id': status_id,
                 'from_created_timestamp': from_created_timestamp,
                 'to_created_timestamp': to_created_timestamp
                 }
            )

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
