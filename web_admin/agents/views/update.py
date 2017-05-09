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
- Init with basic template name "update.html"
# 2017-05-05
-- Load Data
- API 3: GET /api-gateway/agent/v1/agents/{agent_id}
'''
class AgentUpdate( TemplateView ):

    template_name = "update.html"

    def get(self, request, *args, **kwargs):

        context = super(AgentUpdate, self).get_context_data(**kwargs)
        agent_id = context['agent_id']

        # MASTER DATA
        # API 1: Get Agent Types List
        agent_types_list = self._get_agent_types()

        # API 2: Get Currencies List
        currencies = self._get_currencies()

        # LOAD DATA
        # API 3: Get Agent Profile
        agent_profile = self._get_agent_profile(agent_id)

        context = {
            'agent_types': agent_types_list,
            'currencies': currencies,
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

        agent_profile = {}
        if response.status_code != 200:
            logger.info("Getting agent detail got error.")
        else:
            response_json = response.json()
            status = response_json['status']

            if status['code'] == "success":
                agent_profile = response_json.get('data', {})

        logger.info('========== Finish getting agent detail ========== ')

        return agent_profile

    '''
    Author: Steve Le
    History:
    # 2017-05-08
    -- Load Master Data
    - API 1: GET /api-gateway/agent/v1/types
    '''
    def _get_agent_types(self):
        logger.info('========== Start getting agent types list ========== ')

        api_path = settings.GET_AGENT_TYPES_PATH
        url = settings.DOMAIN_NAMES + api_path

        logger.info("API-Path: {}".format(api_path))
        logger.info("Params: {} ")

        headers = get_auth_header(self.request.user)

        start_time = time.time()
        response = requests.get(url, headers=headers, verify=settings.CERT)
        end_time = time.time()

        logger.info("Response_code: {}".format(response.status_code))
        logger.info("Response_content: {}".format(response.content))
        logger.info("Response_time: {} sec.".format(end_time - start_time))

        agent_types_list = {}
        if response.status_code != 200:
            logger.info("Getting agent types list got error.")
        else:
            response_json = response.json()
            status = response_json['status']

            if status['code'] == "success":
                agent_types_list = response_json.get('data', {})

        logger.info('========== Finish getting agent types list ========== ')
        return agent_types_list

    '''
    Author: Steve Le
    History:
    # 2017-05-09
    -- Load Master Data
    - API 2: GET /api-gateway/centralize-configuration/v1/scopes/global/configurations/currency
    '''
    def _get_currencies(self):
        logger.info('========== Start getting currencies list ========== ')

        api_path = settings.GET_CURRENCIES_PATH
        url = settings.DOMAIN_NAMES + api_path

        logger.info("API-Path: {}".format(api_path))
        logger.info("Params: {} ")

        headers = get_auth_header(self.request.user)

        start_time = time.time()
        response = requests.get(url, headers=headers, verify=settings.CERT)
        end_time = time.time()

        logger.info("Response_code: {}".format(response.status_code))
        logger.info("Response_content: {}".format(response.content))
        logger.info("Response_time: {} sec.".format(end_time - start_time))

        currencies = {}
        if response.status_code != 200:
            logger.info("Getting currencies got error.")
        else:
            response_json = response.json()
            status = response_json['status']

            if status['code'] == "success":
                values = response_json.get('data', {}).get('value', '')
                currencies = map(lambda x: x.split('|'), values.split(','))

        logger.info('========== Finish getting currencies list ========== ')
        return currencies