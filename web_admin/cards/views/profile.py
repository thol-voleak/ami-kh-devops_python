import logging
import time
import sys
import requests
from django.conf import settings
from django.shortcuts import render
from django.views.generic.base import TemplateView

from authentications.utils import get_auth_header
from authentications.apps import InvalidAccessToken
from web_admin.api_settings import CARD_LIST_PATH


logger = logging.getLogger(__name__)

IS_STOP = {
    True: 'YES',
    False: 'NO',
}


class ProfileView(TemplateView):
    template_name = "profile.html"

    def post(self, request, *args, **kwargs):
        logger.info('========== Start search card ==========')

        card_identifier = request.POST.get('card_identifier')
        user_id = request.POST.get('user_id')
        user_type = request.POST.get('user_type')

        logger.info('card_identifier: {}'.format(card_identifier))
        logger.info('user_id: {}'.format(user_id))
        logger.info('user_type: {}'.format(user_type))

        body = {}

        if card_identifier is not '':
            body['card_identifier'] = card_identifier
        if user_id is not '':
            body['user_id'] = user_id
        if user_type is not '':
            body['user_type_id'] = int(user_type)

        data = self.get_card_list(body)
        if data is not None:
            result_data = self.format_data(data)
        else:
            result_data = data

        context = {'data': result_data,
                   'card_identifier': card_identifier,
                   'user_id' : user_id,
                   'user_type': int(user_type)
                   }

        logger.info('========== End search card ==========')
        return render(request, 'profile.html', context)

    def get_card_list(self, body):
        url = settings.DOMAIN_NAMES + CARD_LIST_PATH

        logger.info('Call search API to backend service')
        logger.info('API-Path: {};'.format(settings.CARD_LIST_PATH))
        start = time.time()
        logger.info("Request body: {};".format(body))
        auth_request = requests.post(url, headers=get_auth_header(self.request.user), json=body, verify=settings.CERT)
        end = time.time()
        logger.info("Response_code: {};".format(auth_request.status_code))
        logger.info("Response_time: {} sec.".format(end - start))

        json_data = auth_request.json()
        status = json_data.get('status', {})
        code = status.get('code', '')
        if (code == "access_token_expire") or (code== 'access_token_not_found'):
            message = status.get('message', 'Something went wrong.')
            raise InvalidAccessToken(message)
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
            i['is_stopped'] = IS_STOP.get(i.get('is_stopped'))
        return data
