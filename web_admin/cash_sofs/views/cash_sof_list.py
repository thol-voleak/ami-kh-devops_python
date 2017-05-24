from web_admin.api_settings import CASH_SOFS_URL

from django.conf import settings
from django.shortcuts import render
from django.views.generic.base import TemplateView

from authentications.utils import get_auth_header
from authentications.apps import InvalidAccessToken

import logging
import requests
import time

logger = logging.getLogger(__name__)

IS_SUCCESS = {
    True: 'Success',
    False: 'Failed',
}


class CashSOFView(TemplateView):
    template_name = "cash_sof.html"

    def post(self, request, *args, **kwargs):
        logger.info('========== Start search cash source of fund ==========')

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
            body['user_type'] = int(user_type_id)
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

        logger.info('========== End search cash source of fund ==========')
        return render(request, self.template_name, context)

    def get_cash_sof_list(self, body):
        url = settings.DOMAIN_NAMES + CASH_SOFS_URL
        logger.info('Call search cash source of fund API to backend service. API-Path: {}'.format(url))
        start = time.time()
        logger.info("Request body: {};".format(body))
        auth_request = requests.post(url, headers=get_auth_header(self.request.user), json=body, verify=settings.CERT)
        end = time.time()
        logger.info("Response_code: {};".format(auth_request.status_code))
        logger.info("Response_time: {} seconds".format(end - start))

        json_data = auth_request.json()
        status = json_data.get('status', {})
        code = status.get('code', '')

        data = json_data.get('data')
        if auth_request.status_code == 200 and status.get('code') == 'success':
            if (data is not None) and (len(data) > 0):
                logger.info('Cash source of fund found {} records'.format(len(data)))
                return data
        else:
            logger.info('Response_content: {}'.format(auth_request.content))
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                message = status.get('message', 'Something went wrong.')
                raise InvalidAccessToken(message)
            raise Exception(auth_request.content)

    def format_data(self, data):
        for i in data:
            i['is_success'] = IS_SUCCESS.get(i.get('is_success'))
        return data
