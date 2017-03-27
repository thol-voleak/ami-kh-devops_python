from django.views.generic.base import TemplateView
from django.conf import settings
import requests, random, string
from authentications.models import *
import logging, datetime

logger = logging.getLogger(__name__)


class ListView(TemplateView):
    template_name = "agent_type/agent_types_list.html"

    def get_context_data(self, **kwargs):
        logger.info('========== Start getting Agent Types List ==========')
        logger.info('Username {}'.format(self.request.user.username))
        data = self.get_agent_types_list()
        refined_data = _refine_data(data)
        logger.info('========== Finished getting Agent Types List ==========')
        result = {'data': refined_data,
                  'msg': self.request.session.pop('agent_type_create_msg', None),
                  'del_msg': self.request.session.pop('agent_type_delete_msg', None)}

        return result

    def get_agent_types_list(self):
        client_id = settings.CLIENTID
        client_secret = settings.CLIENTSECRET
        url = settings.AGENT_TYPES_LIST_URL
        correlation_id = ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

        auth = Authentications.objects.get(user=self.request.user)
        access_token = auth.access_token

        headers = {
            'content-type': 'application/json',
            'correlation-id': correlation_id,
            'client_id': client_id,
            'client_secret': client_secret,
            'Authorization': 'Bearer ' + access_token,
        }

        logger.info('Getting agent types list from backend')
        logger.info('URL: {}'.format(url))
        auth_request = requests.get(url, headers=headers, verify=False)
        logger.info("Received data with response is {}".format(auth_request.status_code))

        json_data = auth_request.json()
        data = json_data.get('data')
        logger.info('Total count of Agent Types is {}'.format(len(data)))
        if auth_request.status_code == 200:
            if (data is not None) and (len(data) > 0):
                return data

        raise Exception("{}".format(json_data["message"]))


def _refine_data(agent_types_list):
    for agent_type in agent_types_list:
        if (agent_type['created_timestamp'] is not None) and (agent_type['created_timestamp'] != "null"):
            created_at = agent_type['created_timestamp'] / 1000.0
            agent_type['created_timestamp'] = datetime.datetime.fromtimestamp(float(created_at)).strftime(
                '%d-%m-%Y %H:%M %p')

    return agent_types_list
