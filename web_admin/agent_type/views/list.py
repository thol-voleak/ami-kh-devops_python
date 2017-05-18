import datetime
import logging

import requests
from django.conf import settings
from django.views.generic.base import TemplateView

from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header

logger = logging.getLogger(__name__)


class ListView(TemplateView):
    template_name = "agent_type/agent_types_list.html"

    def get_context_data(self, **kwargs):
        logger.info('========== Start getting Agent Types List ==========')
        logger.info('Username {}'.format(self.request.user.username))
        data = self.get_agent_types_list()
        logger.info('========== Finished getting Agent Types List ==========')
        result = {'data': data,
                  'msg': self.request.session.pop('agent_type_create_msg', None),
                  'del_msg': self.request.session.pop('agent_type_delete_msg', None)}

        return result

    def get_agent_types_list(self):
        url = settings.AGENT_TYPES_LIST_URL

        logger.info('Getting agent types list from backend')
        logger.info('URL: {}'.format(url))
        auth_request = requests.get(url, headers=get_auth_header(self.request.user),
                                    verify=settings.CERT)
        
        logger.info("Received data with response is {}".format(auth_request.status_code))

        json_data = auth_request.json()
        data = json_data.get('data')
        if auth_request.status_code == 200:
            if (data is not None) and (len(data) > 0):
                logger.info('Total count of Agent Types is {}'.format(len(data)))
                return data

        if json_data["status"]["code"] == "access_token_expire":
            logger.info("{} for {} username".format(json_data["status"]["message"], self.request.user))
            raise InvalidAccessToken(json_data["status"]["message"])
        else:
            raise Exception("{}".format(json_data["status"]["message"]))
