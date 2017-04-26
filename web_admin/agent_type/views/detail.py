import logging
import time

import requests
from django.conf import settings
from django.views.generic.base import TemplateView

from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header

logger = logging.getLogger(__name__)


class DetailView(TemplateView):
    template_name = "agent_type/agent_type_detail.html"

    def get_context_data(self, **kwargs):
        try:
            logger.info('========== Start getting agent type detail ==========')
            context = super(DetailView, self).get_context_data(**kwargs)
            agent_type_id = context['agentTypeId']

            return self._get_agent_type_detail(agent_type_id)



        except:
            context = {'agent_type_info': {}}
            return context

    def _get_agent_type_detail(self, agent_type_id):

        url = settings.AGENT_TYPE_DETAIL_URL.format(agent_type_id)

        start_date = time.time()
        response = requests.get(url, headers=get_auth_header(self.request.user),
                                verify=settings.CERT)
        logger.info("URL: {}".format(url))
        done = time.time()
        response_json = response.json()
        logger.info("Response content for get agent type detail: {}".format(response_json))
        logger.info("Response time is {} sec.".format(done - start_date))
        logger.info("Response status: {}".format(response.status_code))

        if response_json['status']['code'] == "success":
            logger.info("Client detail was fetched.")
            data = response_json.get('data')
            context = {'agent_type_info': data,
                      'msg': self.request.session.pop('agent_type_update_msg', None)
            }
            logger.info('========== Finished getting agent type detail ==========')
            return context

        if response_json["status"]["message"] == "Invalid access token":
            raise InvalidAccessToken(response_json["status"]["message"])
