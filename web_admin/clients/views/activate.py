from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.base import TemplateView, RedirectView
from django.conf import settings
import requests, random, string, time
from authentications.models import Authentications
from .detail import DetailView
from django.http import HttpResponse
import copy

from authentications.models import *

import logging

logger = logging.getLogger(__name__)


def activate(request, client_id):

    logger.info('========== Start activating client ==========')
    logger.info('The Client to be activated {} client id.'.format(client_id))

    params = {
        'status': 'active',
    }

    try:
        url = settings.ACTIVATE_CLIENT_URL.format(client_id)
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

        data_log = copy.deepcopy(params)
        data_log['client_secret'] = ''
        logger.info("Expected client status {}".format(data_log))

        start_date = time.time()
        response = requests.put(url, headers=headers, json=params, verify=False)
        done = time.time()
        logger.info("Response time is {} sec.".format(done - start_date))

        response_json = response.json()
        status = response_json['status']

        logger.info("Response Code is {}".format(status['code']))

        if response.status_code == 200:
            if status['code'] == "success":
                logger.info("Client was activated.")
                logger.info('========== Finish activating client ==========')
                return HttpResponse(status=200, content=response)
            else:
                logger.info("Error activating Client {}".format(client_id))
                logger.info('========== Finish activating client ==========')
                return HttpResponse(status=500, content=response)
        else:
            logger.info("Error activating Client {}".format(client_id))
            logger.info("Status code {}".format(response.status_code))

            logger.info('========== Finish activating client ==========')
            return HttpResponse(status=response.status_code, content=response)

    except Exception as e:
        logger.info(e)
        logger.info('client_id: ' + client_id)
        logger.info('========== Finish activating client ==========')
        return HttpResponse(status=500, content=e)