from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
import requests, random, string, time
from authentications.models import Authentications
from authentications.apps import InvalidAccessToken

from authentications.models import *

import logging

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
        # client_id = request.POST.get('client_id')
        # client_secret = request.POST.get('client_secret')

        try:
            url = settings.AGENT_TYPE_CREATE_URL
            try:
                auth = Authentications.objects.get(user=request.user)
                access_token = auth.access_token
            except Exception as e:
                raise InvalidAccessToken("{}".format(e))

            correlation_id = ''.join(
                random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

            headers = {
                'content-type': 'application/json',
                'correlation-id': correlation_id,
                'client_id': settings.CLIENTID,
                'client_secret': settings.CLIENTSECRET,
                'Authorization': 'Bearer ' + access_token,
            }

            params = {
                "name": request.POST.get('agent_type_input'),
                "description": request.POST.get('agent_type_description_input'),
            }

            start_date = time.time()
            response = requests.post(url, headers=headers, json=params, verify=False)
            done = time.time()
            logger.info("Response time is {} sec.".format(done - start_date))

            response_json = response.json()
            logger.info(response_json)

            status = response_json['status']
            if status['code'] == "success":
                logger.info("Agent Type was created.")
                logger.info('========== Finish create new agent type ==========')
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
