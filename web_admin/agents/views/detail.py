import logging
import time

import requests
from django.conf import settings
from django.views.generic.base import TemplateView
from multiprocessing import Process, Manager
from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header

logger = logging.getLogger(__name__)

class DetailView(TemplateView):
    template_name = "detail.html"

    def get_context_data(self, **kwargs):
        try:
            logger.info('========== Start getting Agent detail ==========')
            context = super(DetailView, self).get_context_data(**kwargs)
            agent_id = context['agent_id']

            context, status = self._get_agent_detail(agent_id)
            if status:
                agent_type_name, status = self._get_agent_type_name(context['agent']['agent_type_id'])
                if status:
                    context.update({
                        'agent_type_name': agent_type_name
                    })
                else:
                    context.update({
                        'agent_type_name': context.agent.agent_type_id
                    })
            return context
        except:
            context = {'agent': {}}
            return context

    def _get_agent_detail(self, agent_id):
        api_path = settings.AGENT_DETAIL_PATH.format(agent_id=agent_id)
        url = settings.DOMAIN_NAMES + api_path
        logger.info('Getting Agent detail - API-Path: {path}'.format(path=api_path))
        start_date = time.time()
        response = requests.get(url, headers=get_auth_header(self.request.user), verify=settings.CERT)
        done = time.time()
        logger.info('Getting Agent detail - Response_time: {}'.format(done - start_date))
        logger.info('Getting Agent detail - Response_code: {}'.format(response.status_code))
        logger.info('Getting Agent detail - Response_content: {}'.format(response.content))
        response_json = response.json()

        if (response.status_code == 200):
            if (response_json['status']['code'] == "success"):
                data = response_json.get('data')
                context = {'agent': data,
                           'agent_id': agent_id,
                           'msg': self.request.session.pop('agent_registration_msg', None)}
                logger.info('========== Finished getting Agent detail ==========')
                return context, True

        logger.info('========== Finished getting Agent detail ==========')

        if response_json["status"]["code"] == "access_token_expire":
            raise InvalidAccessToken(response_json["status"]["message"])
        else:
            raise Exception("{}".format(response_json["status"]["message"]))

    
    def _get_agent_type_name(self, agent_type_id):
        logger.info('Start getting agent types list from backend')

        url = settings.AGENT_TYPES_LIST_URL
        logger.info('Username {} sends request url: {}'.format(self.request.user.username, url))

        headers = get_auth_header(self.request.user)

        start_date = time.time()
        response = requests.get(url, headers=headers, verify=settings.CERT)
        done = time.time()
        logger.info("Response time is {} sec.".format(done - start_date))
        logger.info("Username {} received response code {}".format(self.request.user.username, response.status_code))
        logger.info("Username {} received response content {}".format(self.request.user.username, response.content))
        logger.info('Finish getting agent types list from backend')

        if response.status_code == 200:
            json_data = response.json()
            status = json_data['status']
            if status['code'] == "success":
                agent_types_list = json_data.get('data', {})
                my_id = int(agent_type_id)
                for x in agent_types_list:
                    if x['id'] == my_id:
                        agent_type_name = x['name']
                        return agent_type_name, True

                return 'Unknown', True
            else:
                return None, False
        else:
            return None, False