import logging
import time

import requests
from django.conf import settings
from django.shortcuts import render
from django.views.generic.base import TemplateView

from authentications.utils import get_auth_header

logger = logging.getLogger(__name__)

IS_SUCCESS = {
    True: 'Success',
    False: 'Failed',
}


class CashTransactionView(TemplateView):
    template_name = "cash_transaction.html"

    def post(self, request, *args, **kwargs):
        logger.info('========== Start search cash transaction ==========')

        sof_id = request.POST.get('sof_id')
        order_id = request.POST.get('order_id')
        type = request.POST.get('type')

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
        url = settings.DOMAIN_NAMES + "api-gateway/report/v1/cash/transactions"

        logger.info('Call search cash source of fund API to backend service. API-Path: {}'.format(url))
        start = time.time()
        logger.info("Request body: {};".format(body))
        auth_request = requests.post(url, headers=get_auth_header(self.request.user), json=body, verify=settings.CERT)
        end = time.time()
        logger.info("Response_code: {};".format(auth_request.status_code))
        logger.info("Response_time: {} seconds".format(end - start))

        json_data = auth_request.json()
        data = json_data.get('data')
        if auth_request.status_code == 200:
            if (data is not None) and (len(data) > 0):
                logger.info('Cash transaction found {} records'.format(len(data)))
                return data
        else:
            logger.info('Response_content: {}'.format(auth_request.content))
            return []

    def format_data(self, data):
        for i in data:
            i['is_stopped'] = IS_SUCCESS.get(i.get('is_stopped'))
        return data
