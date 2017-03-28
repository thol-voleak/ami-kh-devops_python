from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.base import TemplateView
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from authentications.models import Authentications
from authentications.apps import InvalidAccessToken


import requests, random, string, time
import copy
import logging

logger = logging.getLogger(__name__)

class AgentTypeUpdateForm(TemplateView):
    template_name = "agent_type/agent_type_update.html"

    def get_context_data(self, **kwargs):
        try:
            logger.info('========== Start getting agent type detail ==========')

            context = super(AgentTypeUpdateForm, self).get_context_data(**kwargs)
            agent_type_id = context['agentTypeId']

            return self._get_agent_type_detail(agent_type_id)
            # TODO: switch dong tren = 3 dong duoi de test
            # data = {'name': "name_unique", 'description':"description", 'id':agent_type_id}
            # context = {'agent_type_info':data}
            # return context

        except:
            context = {'agent_type_info': {}}
            return context

    def _get_agent_type_detail(self, agent_type_id):

        url = settings.AGENT_TYPE_UPDATE_URL.format(agent_type_id)
        correlation_id = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

        try:
            auth = Authentications.objects.get(user=self.request.user)
            access_token = auth.access_token
        except Exception as e:
            raise InvalidAccessToken("{}".format(e))

        headers = {
            'content-type': 'application/json',
            'correlation-id': correlation_id,
            'client_id': settings.CLIENTID,
            'client_secret': settings.CLIENTSECRET,
            'Authorization': 'Bearer ' + access_token,
        }
        logger.info("Username: {}".format(auth.user))
        logger.info('Getting agent type detail from backend')
        logger.info("URL: {}".format(url))
        start_date = time.time()
        response = requests.get(url, headers=headers, verify=False)
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
                'Authorization': 'Bearer {}'.format(access_token),
            }

            start_time = time.time()

            # TODO: comment the row below
            # return redirect('agent_type:agent-type-detail', agentTypeId=agent_type_id)

            response = requests.put(url, headers=headers, json=params, verify=False)

            logger.info("Response: {}".format(response.content))
            end_time = time.time()
            logger.info("Response time is {} sec.".format(end_time - start_time))

            response_json = response.json()
            status = response_json['status']

            logger.info("Response Code is {}".format(status['code']))

            if response.status_code == 200:
                if status['code'] == "success":
                    logger.info("Agent Type was updated.")
                    logger.info('========== Finished updating Agent Type ==========')
                    request.session['agent_type_update_msg'] = 'Updated agent type successfully'
                    # return redirect('agent_type:agent-type-detail', kwargs=(agentTypeId=agent_type_id))
                    # return HttpResponseRedirect(reverse('agent_type:agent-type-detail', args=(agent_type_id)))
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
