from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger
from web_admin.api_settings import CASH_TRANSACTIONS_URL
from web_admin.restful_methods import RESTfulMethods

from django.shortcuts import render
from django.views.generic.base import TemplateView
from datetime import datetime
from braces.views import GroupRequiredMixin

import logging

logger = logging.getLogger(__name__)

IS_SUCCESS = {
    True: 'Success',
    False: 'Failed',
}


class CashTransactionView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_SEARCH_CASH_TXN"
    login_url = 'authentications:login'
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
        self.logger.info('========== Start search cash transaction ==========')

        search = request.GET.get('search')
        if search is None:
            self.logger.info("Search is none")
            return render(request, self.template_name)

        sof_id = request.GET.get('sof_id')
        order_id = request.GET.get('order_id')
        action_id = request.GET.get('action_id')
        status_id = request.GET.get('status_id')

        self.logger.info('sof_id: {}'.format(sof_id))
        self.logger.info('order_id: {}'.format(order_id))
        self.logger.info('action_id: {}'.format(action_id))
        self.logger.info('status_id: {}'.format(status_id))
        from_created_timestamp = request.GET.get('from_created_timestamp')
        to_created_timestamp = request.GET.get('to_created_timestamp')

        body = {}
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
            logger.info("from_created_timestamp [{}]".format(new_from_created_timestamp))
        if to_created_timestamp is not '' and to_created_timestamp is not None:
            new_to_created_timestamp = datetime.strptime(to_created_timestamp, "%Y-%m-%d")
            new_to_created_timestamp = new_to_created_timestamp.replace(hour=23, minute=59, second=59)
            new_to_created_timestamp = new_to_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['to_created_timestamp'] = new_to_created_timestamp
            logger.info("to_created_timestamp [{}]".format(new_to_created_timestamp))

        self.logger.info("keyword for search is [{}]".format(body))

        data = self.get_cash_transaction_list(body)
        if data is not None:
            result_data = self.format_data(data)
        else:
            result_data = data

        context = {'transaction_list': result_data,
                   'sof_id': sof_id,
                   'order_id': order_id,
                   'action_id': action_id,
                   'status_id': status_id,
                   'from_created_timestamp': from_created_timestamp,
                   'to_created_timestamp': to_created_timestamp
                   }

        self.logger.info('========== End search cash transaction ==========')
        return render(request, self.template_name, context)

    def get_cash_transaction_list(self, body):
        response, status = self._post_method(CASH_TRANSACTIONS_URL, 'Cash Transaction List', logger, body)
        return response

    def format_data(self, data):
        for i in data:
            i['is_success'] = IS_SUCCESS.get(i.get('is_success'))
        return data
