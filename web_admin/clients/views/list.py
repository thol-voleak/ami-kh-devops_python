from django.views.generic.base import TemplateView
from django.conf import settings
from authentications.apps import InvalidAccessToken
from authentications.models import Authentications

import requests
import random
import string
import logging
import datetime


logger = logging.getLogger(__name__)


class ListView(TemplateView):
    template_name = "clients/clients_list.html"

    def get_context_data(self, **kwargs):
        logger.info('========== Start get Clients List ==========')
        data = self.get_clients_list
        refined_data = _refine_data(data)
        logger.info('========== Finished get Clients List ==========')
        result = {'data': refined_data,
                  'msg': self.request.session.pop('client_update_msg', None)}
        return result

    @property
    def get_clients_list(self):
        client_id = settings.CLIENTID
        client_secret = settings.CLIENTSECRET
        url = settings.CLIENTS_LIST_URL
        correlation_id = ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

        try:
            auth = Authentications.objects.get(user=self.request.user)
            access_token = auth.access_token
        except Exception as e:
            raise InvalidAccessToken("{}".format(e))

        headers = {
            'content-type': 'application/json',
            'correlation-id': correlation_id,
            'client_id': client_id,
            'client_secret': client_secret,
            'Authorization': 'Bearer {}'.format(access_token),
        }

        logger.info('Getting client list from backend')
        auth_request = requests.get(url, headers=headers, verify=False)
        logger.info("Received data with response is {}".format(auth_request.status_code))

        json_data = auth_request.json()
        data = json_data.get('data')
        if auth_request.status_code == 200:
            if (data is not None) and (len(data) > 0):
                return data

        if json_data["message"] == "Invalid access token":
            logger.info("{} for {} username".format(json_data["message"], self.request.user))
            raise InvalidAccessToken(json_data["message"])
        else:
            raise Exception('message', auth_request.content)


def _refine_data(clients_list):
    for client in clients_list:
        if (client['created_timestamp'] is not None) and (client['created_timestamp'] != "null"):
            created_at = client['created_timestamp'] / 1000.0
            client['created_timestamp'] = datetime.datetime.fromtimestamp(float(created_at)).strftime(
                '%d-%m-%Y %H:%M %p')

        if (client['last_updated_timestamp'] is not None) and (client['last_updated_timestamp'] != "null"):
            created_at = client['last_updated_timestamp'] / 1000.0
            client['last_updated_timestamp'] = datetime.datetime.fromtimestamp(float(created_at)).strftime(
                '%d-%m-%Y %H:%M %p')
    return clients_list
