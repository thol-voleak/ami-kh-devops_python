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


class PaymentOrderView(TemplateView):
    template_name = "payment_order.html"

    def post(self, request, *args, **kwargs):
        logger.info('========== Start search cash source of fund ==========')

        order_id = request.POST.get('order_id')
        service_name = request.POST.get('service_name')
        payer_user_id = request.POST.get('payer_user_id')
        payer_user_type_id = request.POST.get('payer_user_type_id')
        payee_user_id = request.POST.get('payee_user_id')
        payee_user_type_id = request.POST.get('payee_user_type_id')

        logger.info('order_id: {}'.format(order_id))
        logger.info('service_name: {}'.format(service_name))
        logger.info('payer_user_id: {}'.format(payer_user_id))
        logger.info('payer_user_type_id: {}'.format(payer_user_type_id))
        logger.info('payee_user_id: {}'.format(payee_user_id))
        logger.info('payee_user_type_id: {}'.format(payee_user_type_id))

        body = {}
        if order_id is not '':
            body['order_id'] = order_id
        if service_name is not '':
            body['service_name'] = service_name
        if payer_user_id is not '':
            body['payer_user_id'] = payer_user_id
        if payer_user_type_id is not '' and payer_user_type_id is not '0':
            body['payer_user_type_id'] = int(payer_user_type_id)
        if payee_user_id is not '':
            body['payee_user_id'] = payee_user_id
        if payee_user_type_id is not '' and payee_user_type_id is not '0':
            body['payee_user_type_id'] = int(payee_user_type_id)

        data = self.get_payment_order_list(body)
        if data is not None:
            result_data = self.format_data(data)
        else:
            result_data = data

        context = {'order_list': result_data,
                   'order_id': order_id,
                   'service_name': service_name,
                   'payer_user_id': payer_user_id,
                   'payer_user_type_id':payer_user_type_id,
                   'payee_user_id': payee_user_id,
                   'payee_user_type_id':payee_user_type_id,
                   }

        logger.info('========== End search cash source of fund ==========')
        return render(request, self.template_name, context)

    def get_payment_order_list(self, body):
        url = settings.DOMAIN_NAMES + "api-gateway/report/v1/payments/orders"

        logger.info('Call search payment order API to backend service. API-Path: {}'.format(url))
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
                logger.info('Payment order found [{}] records'.format(len(data)))
                return data
        else:
            logger.info('Response_content: {}'.format(auth_request.content))
            raise Exception(auth_request.content)

    def format_data(self, data):
        for i in data:
            i['is_stopped'] = IS_SUCCESS.get(i.get('is_stopped'))
        return data
