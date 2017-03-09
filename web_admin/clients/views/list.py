from django.views.generic.base import TemplateView
from django.conf import settings
import requests, random, string

from authentications.models import *

import logging, datetime

logger = logging.getLogger(__name__)


class ListView(TemplateView):
    template_name = "clients/clients_list.html"

    def get_context_data(self, **kwargs):
        try:
            logger.info('========== Start get Clients List ==========')

            data = self._get_clients_list()

            refined_data = self._refine_data(data)
            context = {'data': refined_data}
            logger.info('========== Finished get Clients List ==========')

            return context
        except:
            return None

    def _refine_data(self, clients_list):
        logger.info("Setting datetime format with dd-mm-yy hh:mm")
        for client in clients_list:
            # Format Creation Date
            if (client['created_timestamp'] is not None) and (client['created_timestamp'] != "null"):
                created_at = client['created_timestamp'] / 1000.0
                client['created_timestamp'] = datetime.datetime.fromtimestamp(float(created_at)).strftime(
                    '%d-%m-%Y %H:%M')

            # Format Modification Date
            if (client['last_updated_timestamp'] is not None) and (client['last_updated_timestamp'] != "null"):
                created_at = client['last_updated_timestamp'] / 1000.0
                client['last_updated_timestamp'] = datetime.datetime.fromtimestamp(float(created_at)).strftime(
                    '%d-%m-%Y %H:%M')
        logger.info("Data was set datetime with dd-mm-yy hh:mm format")
        return clients_list

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

        logger.info('Getting client list from backend')
        auth_request = requests.get(url, params=payload, headers=headers, verify=False)
        logger.info("Received data with response status is {}".format(auth_request.status_code))

        json_data = auth_request.json()
        data = json_data.get('data')

        if (data is not None) and (len(data) > 0):
            return data
        else:
            return None
