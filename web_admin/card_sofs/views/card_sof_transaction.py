from web_admin import setup_logger, api_settings
from web_admin.restful_methods import RESTfulMethods

from datetime import datetime
from django.conf import settings
from django.views.generic.base import TemplateView
from django.shortcuts import render
from authentications.utils import get_correlation_id_from_username

import logging

logger = logging.getLogger(__name__)


class CardSOFTransaction(TemplateView, RESTfulMethods):

    raise_exception = False

    template_name = "sof/card_sof_transaction.html"
    search_card_transaction = settings.DOMAIN_NAMES + "api-gateway/report/"+api_settings.API_VERSION+"/cards/transactions"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CardSOFTransaction, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start search card sof transaction history ==========')
        self.logger.info(self.search_card_transaction)


        sof_id = request.POST.get('sof_id')
        order_id = request.POST.get('order_id')
        status = request.POST.get('status')
        type = request.POST.get('type')
        from_created_timestamp = request.POST.get('from_created_timestamp')
        to_created_timestamp = request.POST.get('to_created_timestamp')

        self.logger.info('Search key "sof_id is" is [{}]'.format(sof_id))
        self.logger.info('Search key "order_id" is [{}]'.format(order_id))
        self.logger.info('Search key "type" is [{}]'.format(type))
        self.logger.info('Search key "status" is [{}]'.format(status))
        self.logger.info('Search key "from_created_timestamp" is [{}]'.format(from_created_timestamp))
        self.logger.info('Search key "to_created_timestamp" is [{}]'.format(to_created_timestamp))


        body = self.createSearchBody(from_created_timestamp, order_id, sof_id, status, to_created_timestamp, type)

        responses, success = self._get_card_sof_transaction(body=body)

        context = {
            'transaction_list': responses,
            'search_by': body,
            'from_created_timestamp': from_created_timestamp,
            'to_created_timestamp': to_created_timestamp
        }

        self.logger.info('========== End search card sof transaction history ==========')
        return render(request, self.template_name, context)

    def createSearchBody(self, from_created_timestamp, order_id, sof_id, status, to_created_timestamp, type):
        body = {}

        return body
    def _get_card_sof_transaction(self, body):
        return self._post_method(self.search_card_transaction, 'Card Source of Fund List', logger, body)
