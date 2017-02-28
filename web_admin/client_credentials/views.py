from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.apps import AppConfig
from authentications.models import Authentications
from django.conf import settings
import requests, json, random, string

from authentications.models import *

import logging

logger = logging.getLogger(__name__)

class NoDataAvailable(Exception):
    pass

def get_clients_list():
    client_id = settings.CLIENTID
    client_secret = settings.CLIENTSECRET
    url = settings.CLIENTS_LIST_URL
    correlation_id = ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

    auth = Authentications.objects.all()
    access_token = auth[0].access_token

    payload = {}
    headers = {
        'content-type': 'application/json',
        'correlation-id': correlation_id,
        'client_id': client_id,
        'client_secret': client_secret,
        'Authorization': 'Bearer ' + access_token,
    }

    logger.info('GET api gateway: /v1/oauths/clients')
    auth_request = requests.get(url, params=payload, headers=headers)
    logger.info("response {}".format(auth_request.content))
    logger.info('Check response success or fail')
    json_data = auth_request.json()
    data = json_data.get('data')

    if (data is not None) and (len(data) > 0):
        return data
    else:
        raise NoDataAvailable()


@login_required(login_url='login')
def index(request):
    try:
        logger.info('========== Get Clients List ==========')

        data = get_clients_list()
        logger.info('Data is available for usage')
        context = {'clients_list': data}
        return render(request, 'client_credentials/clients_list.html', context)
    except:
        return None
