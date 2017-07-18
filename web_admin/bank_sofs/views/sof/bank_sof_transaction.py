from web_admin import setup_logger
from web_admin.restful_methods import RESTfulMethods

from datetime import datetime
from django.conf import settings
from django.views.generic.base import TemplateView
from django.shortcuts import render
from authentications.utils import get_correlation_id_from_username
import logging

logger = logging.getLogger(__name__)


class BankSOFTransaction(TemplateView, RESTfulMethods):
    template_name = "sof/bank_transaction.html"
    search_bank_transaction = settings.DOMAIN_NAMES + "api-gateway/report/v1/banks/transactions"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(BankSOFTransaction, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start search bank transaction history ==========')
        self.logger.info(self.search_bank_transaction)
        search = request.GET.get('search')
        if search is None:
            self.logger.info("Search is none")
            return render(request, self.template_name)

        sof_id = request.GET.get('sof_id')
        order_id = request.GET.get('order_id')
        status = request.GET.get('status')
        type = request.GET.get('type')
        from_created_timestamp = request.GET.get('from_created_timestamp')
        to_created_timestamp = request.GET.get('to_created_timestamp')

        self.logger.info('Search key "sof_id is" is [{}]'.format(sof_id))
        self.logger.info('Search key "order_id" is [{}]'.format(order_id))
        self.logger.info('Search key "type" is [{}]'.format(type))
        self.logger.info('Search key "status" is [{}]'.format(status))
        self.logger.info('Search key "from_created_timestamp" is [{}]'.format(from_created_timestamp))
        self.logger.info('Search key "to_created_timestamp" is [{}]'.format(to_created_timestamp))


        body = self.createSearchBody(from_created_timestamp, order_id, sof_id, status, to_created_timestamp, type)

        responses, success = self._get_sof_bank_transaction(body=body)

        context = {
            'transaction_list': responses,
            'search_by': body,
            'from_created_timestamp': from_created_timestamp,
            'to_created_timestamp': to_created_timestamp
        }

        self.logger.info('========== Start search bank transaction history ==========')
        return render(request, self.template_name, context)

    def createSearchBody(self, from_created_timestamp, order_id, sof_id, status, to_created_timestamp, type):
        body = {}
        if sof_id is not '' and sof_id is not None:
            body['sof_id'] = int(sof_id)
        if order_id is not '' and order_id is not None:
            body['order_id'] = order_id
        if status is not '' and status is not None:
            body['status_id'] = int(status)
        if type is not '' and type is not None:
            body['action_id'] = int(type)
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
        return body
    def _get_sof_bank_transaction(self, body):
        return self._post_method(self.search_bank_transaction, 'Cash Source of Fund List', logger, body)
