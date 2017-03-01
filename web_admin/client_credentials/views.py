from django.views.generic.base import TemplateView
from django.conf import settings
import requests, json, random, string

from authentications.models import *

import logging, datetime

logger = logging.getLogger(__name__)


class ListView(TemplateView):
    template_name = "client_credentials/clients_list.html"

    def get_context_data(self, **kwargs):
        try:
            logger.info('========== Get Clients List ==========')

            data = self._get_clients_list()

            logger.info('Refine Clients List')
            refined_data = self._refine_data(data)
            context = {'data': refined_data}
            logger.info('========== Got Clients List ==========')
            return context
        except:
            return None

    def _refine_data(self, client_list):

        for client in client_list:

            # Format Creation Date
            if client['created_timestamp'] is not None:
                created_at = client['created_timestamp'] / 1000.0
                client['created_timestamp'] = datetime.datetime.fromtimestamp(float(created_at)).strftime('%d-%m-%Y %H:%M')

            # Format Modification Date
            if client['last_updated_timestamp'] is not None:
                created_at = client['last_updated_timestamp'] / 1000.0
                client['last_updated_timestamp'] = datetime.datetime.fromtimestamp(float(created_at)).strftime(
                    '%d-%m-%Y %H:%M')

            # Set it blank
            for k, v in client.iteritems():
                if v is None:
                    client[k] = ''

        return client_list


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
