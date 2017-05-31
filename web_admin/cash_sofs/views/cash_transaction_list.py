import logging

from web_admin.api_settings import CASH_TRANSACTIONS_URL
from web_admin.restful_methods import RESTfulMethods
from django.shortcuts import render
from django.views.generic.base import TemplateView


logger = logging.getLogger(__name__)

IS_SUCCESS = {
    True: 'Success',
    False: 'Failed',
}


class CashTransactionView(TemplateView, RESTfulMethods):
    template_name = "cash_transaction.html"

    def get(self, request, *args, **kwargs):
        logger.info('========== Start search cash transaction ==========')

        sof_id = request.GET.get('sof_id')
        order_id = request.GET.get('order_id')
        type = request.GET.get('type')

        logger.info('sof_id: {}'.format(sof_id))
        logger.info('order_id: {}'.format(order_id))
        logger.info('type: {}'.format(type))

        body = {}
        if sof_id is not '':
            body['sof_id'] = sof_id
        if order_id is not '':
            body['order_id'] = order_id
        if type is not '':
            body['type'] = type

        data = self.get_cash_transaction_list(body)
        if data is not None:
            result_data = self.format_data(data)
        else:
            result_data = data

        context = {'transaction_list': result_data,
                   'sof_id': sof_id,
                   'order_id': order_id,
                   'type': type
                   }

        logger.info('========== End search cash transaction ==========')
        return render(request, self.template_name, context)

    def get_cash_transaction_list(self, body):
        response, status = self._post_method(CASH_TRANSACTIONS_URL, 'Cash Transaction List', logger, body)
        return response

    def format_data(self, data):
        for i in data:
            i['is_success'] = IS_SUCCESS.get(i.get('is_success'))
        return data
