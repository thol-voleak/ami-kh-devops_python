from authentications.apps import InvalidAccessToken
from authentications.models import *

import logging
import random
import string
import time
import requests

from django.conf import settings
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

logger = logging.getLogger(__name__)


class DeleteView(TemplateView):
    template_name = "agent_type/agent_type_delete.html"

    def get_context_data(self, **kwargs):
        try:
            logger.info('========== Start getting agent type detail ==========')
            context = super(DeleteView, self).get_context_data(**kwargs)
            agent_type_id = context['agent_type_id']

            return self._get_agent_type_detail(agent_type_id)
        except:
            context = {'agent_type_info': {}}
            return context

    def _get_agent_type_detail(self, agent_type_id):

        url = settings.AGENT_TYPE_DETAIL_URL.format(agent_type_id)
        correlation_id = ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

        try:
            auth = Authentications.objects.get(user=self.request.user)
            logger.info("Username: {}".format(self.request.user.username))
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

        start_date = time.time()
        response = requests.get(url, headers=headers, verify=False)
        logger.info("URL: {}".format(url))
        done = time.time()
        response_json = response.json()
        logger.info("Response content for get agent type detail: {}".format(response_json))
        logger.info("Response time is {} sec.".format(done - start_date))
        logger.info("Response status: {}".format(response.status_code))

        if response_json['status']['code'] == "success":
            logger.info("agent type detail was fetched.")
            data = response_json.get('data')
            context = {'agent_type_info': data}
            logger.info('========== Finished getting agent type detail ==========')
            return context

        if response_json["message"] == "Invalid access token":
            raise InvalidAccessToken(response_json["message"])


def delete_agent_type(request, agent_type_id):
    try:
        logger.info("========== Start deleting agent type ==========")
        logger.info('Agent Type ID to be deleted: {}'.format(agent_type_id))
        logger.info('Username: {}'.format(request.user.username))

        url = settings.DELETE_AGENT_TYPE_URL.format(agent_type_id)
        auth = Authentications.objects.get(user=request.user)
        access_token = auth.access_token

        correlation_id = ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

        headers = {
            'content-type': 'application/json',
            'correlation-id': correlation_id,
            'client_id': settings.CLIENTID,
            'client_secret': settings.CLIENTSECRET,
            'Authorization': 'Bearer {}'.format(access_token),
        }

        logger.info('URL: {}'.format(url))
        start_date = time.time()
        response = requests.delete(url, headers=headers, verify=False)
        done = time.time()
        logger.info("Response time for delete {} agent type id is {} sec.".format(agent_type_id, done - start_date))
        logger.info("Response for delete {} agent type id is {}".format(agent_type_id, response.content))
        logger.info("Response Code is {}".format(response.status_code))

        if response.status_code == 200:
            response_json = response.json()
            status = response_json['status']
            if status['code'] == "success":
                logger.info("Agent Type was deleted.")
                logger.info("========== Finished deleting agent type id ==========")
                request.session['agent_type_delete_msg'] = 'Deleted data successfully'
                return HttpResponseRedirect(reverse('agent_type:agent-type-list', args=(None)))
            else:
                logger.info("Error deleting agent type {}".format(agent_type_id))
                logger.info("========== Finished deleting agent type id ==========")
                raise Exception("{}".format(status["message"]))
        else:
            logger.info("Error deleting agent type {}".format(agent_type_id))
            logger.info("========== Finished deleting agent type id ==========")
            raise Exception("{}".format(response.content))

    except Exception as e:
        logger.info('Exception:')
        logger.info(e)
        logger.info("========== Finished deleting agent type id ==========")
        raise Exception("{}".format(e))
