import logging
import time

import requests
from django.conf import settings
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.base import TemplateView

from authentications.utils import get_auth_header

logger = logging.getLogger(__name__)


class AgentTypeUpdateForm(TemplateView):
    template_name = "agent_type/agent_type_update.html"

    def get_context_data(self, **kwargs):
        try:
            logger.info('========== Start getting agent type detail ==========')

            context = super(AgentTypeUpdateForm, self).get_context_data(**kwargs)
            agent_type_id = context['agentTypeId']

            return self._get_agent_type_detail(agent_type_id)
        except:
            context = {'agent_type_info': {}}
            return context

    def _get_agent_type_detail(self, agent_type_id):

        url = settings.AGENT_TYPE_UPDATE_URL.format(agent_type_id)
        logger.info("Username: {}".format(self.request.user.username))
        logger.info('Getting agent type detail from backend')
        logger.info("URL: {}".format(url))
        start_date = time.time()
        response = requests.get(url, headers=get_auth_header(self.request.user),
                                verify=settings.CERT)
        logger.info("Response Content: {}".format(response.content))
        done = time.time()
        logger.info("Response time is {} sec.".format(done - start_date))
        logger.info("Received data with response status is {}".format(response.status_code))

        response_json = response.json()
        if response_json['status']['code'] == "success":
            logger.info("Agent type detail was fetched.")
            data = response_json.get('data')
            context = {'agent_type_info': data}
            return context
        else:
            logger.info("Error Getting Agent Type Detail.")
            context = {'agent_type_info': response_json.get('data')}
            return context


class AgentTypeUpdate(View):
    @staticmethod
    def post(request, *args, **kwargs):

        logger.info('Start updating agent type')
        agent_type_id = kwargs['agentTypeId']
        url = settings.AGENT_TYPE_UPDATE_URL.format(agent_type_id)
        logger.info("URL: {}".format(url))

        name = request.POST.get('agent_type_input')
        description = request.POST.get('agent_type_description_input')
        params = {
            "name": name,
            "description": description,
        }
        logger.info('PUT Request: {}'.format(params))

        try:

            start_time = time.time()
            response = requests.put(url, headers=get_auth_header(request.user),
                                    json=params, verify=settings.CERT)
            end_time = time.time()
            logger.info("Response: {}".format(response.content))
            logger.info("Response time is {} sec.".format(end_time - start_time))

            response_json = response.json()
            status = response_json['status']

            logger.info("Response Code is {}".format(status['code']))

            if response.status_code == 200:
                if status['code'] == "success":
                    logger.info("Agent Type was updated.")
                    logger.info('========== Finished updating Agent Type ==========')
                    request.session['agent_type_update_msg'] = 'Updated agent type successfully'
                    return redirect('agent_type:agent-type-detail', agentTypeId=(agent_type_id))
                else:
                    logger.info("Error Updating Agent {}".format(agent_type_id))
                    context = {'agent_type_info': params}
                    logger.info('========== Finish updating agent type ==========')
                    return render(request, 'agent_type/agent_type_update.html', context)
            else:
                logger.info("Error Updating Agent Type {}".format(agent_type_id))
                logger.info("Status code {}".format(response.status_code))
                context = {'agent_type_info': params}
                logger.info('========== Finish updating agent type ==========')
                return render(request, 'agent_type/agent_type_update.html', context)

        except Exception as e:
            logger.info(e)
            logger.info('agent_type.id: ' + agent_type_id)
            context = {'agent_type_info': params}
            logger.info('========== Finish updating agent type ==========')
            return render(request, 'agent_type/agent_type_update.html', context)
