from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.apps import AppConfig
from web_admin.authentications.models import Authentications
from django.conf import settings
import requests, json, random, string

import logging

logger = logging.getLogger(__name__)

# from .models import Choice, Question
# from django.db.models import F, Count

# Create your views here.

class NoDataAvailable(Exception):
    pass

def get_clients_list():

     client_id = settings.CLIENTID
     client_secret = settings.CLIENTSECRET
     url = settings.CLIENTS_LIST_URL
     correlation_id = ''.join(
          random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

     auth = Authentications.objects.all()
     access_token = auth.access_token

     payload = {}
     headers = {
          'content-type': 'application/json',
          'correlation-id': correlation_id,
          'client_id': client_id,
          'client_secret': client_secret,
          'Authorization': access_token,
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
          context = {'data': data}
          return render(request, 'client_credentials/clients_list.html', context)

     except NoDataAvailable:
          logger.info('No Data Available or Error occurred.')
          return None

     except ValueError:
          logger.info('No JSON object could be decoded.')
          return None

     except requests.exceptions.Timeout:
          logger.info('Timeout')
          return None

     except requests.exceptions.TooManyRedirects:
          logger.info('TooManyRedirects')
          return None

     except requests.exceptions.RequestException as e:
          logger.info('RequestException')
          return None

