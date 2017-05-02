from django.views.generic.base import TemplateView
from django.conf import settings

import requests
import logging
import datetime

from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header

logger = logging.getLogger(__name__)


class ListView(TemplateView):
    template_name = "clients/clients_list.html"

    def get_context_data(self, **kwargs):
        logger.info('========== Start get Clients List ==========')
        data = self.get_clients_list
        logger.info('========== Finished get Clients List ==========')
        result = {'data': data,
                  'msg': self.request.session.pop('client_update_msg', None)}
        return result

    def get_clients_list(self):
        url = settings.CLIENTS_LIST_URL
        headers = get_auth_header(self.request.user)

        logger.info('Getting client list from backend')
        auth_request = requests.get(url, headers=headers, verify=settings.CERT)
        logger.info("Received data with response is {}".format(auth_request.status_code))

        json_data = auth_request.json()
        data = json_data.get('data')
        if auth_request.status_code == 200:
            logger.info('Total count of client list is {}'.format(len(data)))
            return data

        if json_data["status"]["code"] == "access_token_expire":
            logger.info("{} for {} username".format(json_data["status"]["message"], self.request.user))
            raise InvalidAccessToken(json_data["status"]["message"])
        else:
            raise Exception("{}".format(json_data["status"]["message"]))
