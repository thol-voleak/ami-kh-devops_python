import logging
import time

import requests
from django.conf import settings
from django.shortcuts import redirect, render
from django.views import View

from authentications.utils import get_auth_header

logger = logging.getLogger(__name__)


class AgentTypeCreate(View):
    @staticmethod
    def get(request, *args, **kwargs):
        agent_type_info = {
            "agent_type_input": None,
            "agent_type_description_input": None,
        }
        context = {'agent_type_info': agent_type_info,
                   'error_msg': None}

        return render(request, 'agent_type/create_agent_type.html', context)

    @staticmethod
    def post(request, *args, **kwargs):
        logger.info('========== Start creating new agent type ==========')

        try:
            url = settings.AGENT_TYPE_CREATE_URL

            params = {
                "name": request.POST.get('agent_type_input'),
                "description": request.POST.get('agent_type_description_input'),
            }

            logger.info("URL: {}".format(url))
            logger.info("Request: {}".format(params))

            start_date = time.time()
            response = requests.post(url, headers=get_auth_header(request.user),
                                     json=params, verify=settings.CERT)
            done = time.time()
            logger.info("Response time is {} sec.".format(done - start_date))

            response_json = response.json()
            logger.info("Response content: {}".format(response_json))
            logger.info("Response status: {}".format(response.status_code))
            status = response_json['status']
            if status['code'] == "success":
                logger.info("Agent Type was created.")
                logger.info('========== Finish create new agent type ==========')
                request.session['agent_type_create_msg'] = 'Added data successfully'
                return redirect('agent_type:agent-type-list')
            else:
                logger.info("Error Creating Agent Type.")
                context = {'client_info': params,
                           'error_msg': response_json['status']['message']}
                logger.info('========== Finish create new agent type ==========')
                return render(request, 'agent_type/agent_types_list.html', context)

        except Exception as e:
            logger.info(e)
            client_info = {
                "client_id": settings.CLIENTID,
                "client_secret": settings.CLIENTSECRET,
                "agent_type_input": None,
                "agent_type_description_input": None,
            }
            context = {'client_info': client_info, 'error_msg': None}
            logger.info('========== Finish create new agent type ==========')
            return render(request, 'agent_type/agent_types_list.html', context)
