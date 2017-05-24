from web_admin.api_settings import CASH_TRANSACTIONS_URL

from django.conf import settings
from django.shortcuts import render
from django.views.generic.base import TemplateView
from authentications.utils import get_auth_header
from authentications.apps import InvalidAccessToken

import requests
import logging
import time

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
        url = settings.DOMAIN_NAMES + CASH_TRANSACTIONS_URL

        logger.info(
            'Call search cash source of fund API to backend service. API-Path: {}'.format(url))
        start = time.time()
        logger.info("Request body: {}".format(body))
        responses = requests.post(url,
                                  headers=get_auth_header(self.request.user),
                                  json=body,
                                  verify=settings.CERT)
        end = time.time()
        logger.info("Response_code: {}".format(responses.status_code))
        logger.info("Response_time: {} seconds".format(end - start))

        json_data = responses.json()
        status = json_data.get('status', {})
        code = status.get('code', '')

        if responses.status_code == 200:
            data = json_data.get('data')
            if data is not None and len(data) > 0:
                logger.info('Cash transaction found {} records'.format(len(data)))
                return data
        else:
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                message = status.get('message', 'Something went wrong.')
                raise InvalidAccessToken(message)

            logger.info('Response_content: {}'.format(responses.content))
            raise Exception(responses.content)

    def format_data(self, data):
        for i in data:
            i['is_success'] = IS_SUCCESS.get(i.get('is_success'))
        return data
