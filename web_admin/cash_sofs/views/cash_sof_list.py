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


class CashSOFView(TemplateView):
    template_name = "cash_sof.html"

    def post(self, request, *args, **kwargs):
        logger.info('========== Start search history card ==========')

        user_id = request.POST.get('user_id')
        user_type_id = request.POST.get('user_type_id')
        currency = request.POST.get('currency')

        logger.info('user_id: {}'.format(user_id))
        logger.info('user_type_id: {}'.format(user_type_id))
        logger.info('currency: {}'.format(currency))

        body = {}
        if user_id is not '':
            body['user_id'] = user_id
        if user_type_id is not '' and user_type_id is not '0':
            body['user_type_id'] = int(user_type_id)
        if currency is not '':
            body['currency'] = currency

        data = self.get_cash_sof_list(body)
        if data is not None:
            result_data = self.format_data(data)
        else:
            result_data = data

        context = {'sof_list': result_data,
                   'user_id': user_id,
                   'user_type_id': user_type_id,
                   'currency': currency
                   }

        logger.info('========== End search card history ==========')
        return render(request, self.template_name, context)

    def get_cash_sof_list(self, body):
        url = settings.DOMAIN_NAMES + "api-gateway/report/v1/cash/sofs"

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
                logger.info('Cash source of fund found {} records'.format(len(data)))
                return data
        else:
            logger.info('Response_content: {}'.format(auth_request.content))
            return []

    def format_data(self, data):
        for i in data:
            i['is_stopped'] = IS_STOP.get(i.get('is_stopped'))
        return data
