import logging
import time

import requests
from django.conf import settings
from django.views.generic.base import TemplateView

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
            return self._get_agent_detail(agent_id)
        except:
            context = {'agent_info': {}}
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
                return context

        logger.info('========== Finished getting Agent detail ==========')

        if response_json["status"]["code"] == "access_token_expire":
            raise InvalidAccessToken(response_json["status"]["message"])
        else:
            raise Exception("{}".format(response_json["status"]["message"]))

