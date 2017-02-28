from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.conf import settings
import requests, json, random, string

from authentications.models import *

import logging

logger = logging.getLogger(__name__)


class ListView(TemplateView):
    template_name = "client_credentials/clients_list.html"

    def get_context_data(self, **kwargs):
        try:
            logger.info('========== Get Clients List ==========')

            data = self._get_clients_list()
            context = {'data': data}
            logger.info('========== Got Clients List ==========')
            return context
        except:
            return None

    def _get_clients_list(self):
        client_id = settings.CLIENTID
        client_secret = settings.CLIENTSECRET
        url = settings.CLIENTS_LIST_URL
        correlation_id = ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

        auth = Authentications.objects.get(user=self.request.user)
        access_token = auth.access_token

        payload = {}
        headers = {
            'content-type': 'application/json',
            'correlation-id': correlation_id,
            'client_id': client_id,
            'client_secret': client_secret,
            'Authorization': access_token,
            # 'Authorization': 'Bearer ' + access_token,
        }

        logger.info('GET api gateway: /v1/oauths/clients')
        auth_request = requests.get(url, params=payload, headers=headers)
        logger.info("response {}".format(auth_request.content))
        logger.info('Check response success or fail')
        json_data = auth_request.json()
        data = json_data.get('data')

        if (data is not None) and (len(data) > 0):
            return data
        else:
            return None
