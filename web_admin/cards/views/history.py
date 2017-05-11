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



class HistoryView(TemplateView):
    template_name = "history.html"

    def post(self, request, *args, **kwargs):
        logger.info('========== Start search history card ==========')

        trans_id = request.POST.get('trans_id')
        card_id = request.POST.get('card_id')

        logger.info('trans_id: {}'.format(trans_id))
        logger.info('card_id: {}'.format(card_id))

        body = {}
        if trans_id is not '':
            body['trans_id'] = trans_id
        if trans_id is not '':
            body['card_id'] = int(card_id)

        data = self.get_card_history_list(body)
        if data is not None:
            result_data = self.format_data(data)
        else:
            result_data = data

        context = {'data': result_data,
                   'trans_id': trans_id,
                   'card_id': int(card_id)
                   }

        logger.info('========== End search card history ==========')
        return render(request, 'history.html', context)

    def get_card_history_list(self, body):
        url = settings.DOMAIN_NAMES + settings.CARD_HISTORY_PATH

        logger.info('Call search card history API to backend service')
        logger.info('API-Path: {};'.format(settings.CARD_LIST_PATH))
        start = time.time()
        logger.info("Request body: {};".format(body))
        auth_request = requests.post(url, headers=get_auth_header(self.request.user), json=body, verify=settings.CERT)
        end = time.time()
        logger.info("Response_code: {};".format(auth_request.status_code))
        logger.info("Response_time: {} sec.".format(end - start))

        json_data = auth_request.json()
        data = json_data.get('data')
        if auth_request.status_code == 200:
            if (data is not None) and (len(data) > 0):
                logger.info('Card count: {};'.format(len(data)))
                return data
        else:
            logger.info('Response_content: {}'.format(auth_request.content))
            return []

    def format_data(self, data):
        for i in data:
            i['is_success'] = IS_SUCCESS.get(i.get('is_success'))
        return data
