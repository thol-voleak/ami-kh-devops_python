from django.views.generic.base import TemplateView

from django.conf import settings
from authentications.utils import get_auth_header
from django.shortcuts import redirect, render
from django.contrib import messages

import requests, time, logging

logger = logging.getLogger(__name__)

'''
Author: Steve Le
History:
# 2017-05-04 
- Init with basic template name
-- Master Data --
- API 1: GET ...
- API 2: GET ...
-- Load Data --
- API 3: GET /api-gateway/agent/v1/agents/{agent_id}
- API 4
- API 5;
-- Update Data --
- API 6
'''
class AgentUpdate(TemplateView):
    template_name = "update.html"

    def get(self, request, *args, **kwargs):

        context = super(AgentUpdate, self).get_context_data(**kwargs)
        agent_id = context['AgentId']

        # API 1: Get Agent Type List

        # API 2: Get Currency List

        # API 3: Get Agent Profile
        agent_profile = self._get_agent_profile(agent_id)

        context = {
            'agent_profile': agent_profile
        }

        return render(request, self.template_name, context)

    def _get_agent_profile(self, agent_id):
        logger.info('========== Start getting agent detail ========== ')

        api_path = settings.AGENT_DETAIL_PATH.format(agent_id=agent_id)
        url = settings.DOMAIN_NAMES + api_path

        logger.info("API-Path: {}".format(api_path))
        logger.info("Params: agent_id = {} ".format(agent_id))

        headers = get_auth_header(self.request.user)

        start_time = time.time()
        response = requests.get(url, headers=headers, verify=settings.CERT)
        end_time = time.time()

        logger.info("Response_code: {}".format(response.status_code))
        logger.info("Response_content: {}".format(response.content))
        logger.info("Response_time: {} sec.".format(end_time - start_time))

        if response.status_code != 200:
            logger.info("Getting agent detail got error.")
        else:
            response_json = response.json()
            data = response_json.get('data')

        logger.info('========== Finish getting agent detail ========== ')

        return data