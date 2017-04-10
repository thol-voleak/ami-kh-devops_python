from django.shortcuts import render, redirect
from django.views import View
from authentications.models import *

import requests
import random
import string
import time
import copy

from django.conf import settings
from django.http import HttpResponse
from authentications.apps import InvalidAccessToken

import logging

logger = logging.getLogger(__name__)


class CountryCode(View):
    @staticmethod
    def get(request, *args, **kwargs):

        try:
            logger.info('========== Start getting global configurations ==========')

            url = settings.GLOBAL_CONFIGURATIONS_URL
            correlation_id = ''.join(
                random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

            logger.info('Username: {}'.format(request.user.username))
            logger.info('Request URL: {}'.format(url))

            try:
                auth = Authentications.objects.get(user=request.user)
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

            logger.info('Sending request to API-Gateway')
            start_date = time.time()
            response = requests.get(url, headers=headers, verify=settings.CERT)
            done = time.time()

            response_json = response.json()
            context = None

            logger.info("Response time is {} sec.".format(done - start_date))
            logger.info("Received data with response status is {}".format(response.status_code))
            logger.info('Response Content: {}'.format(response_json))

            if response.status_code == 200:

                if response_json['status']['code'] == "success":
                    logger.info("Global configuration was fetched.")
                    data = response_json.get('data')
                    context = {'country_code': response_json['data']['country']}
                else:
                    context = {'country_code': None}

            else:
                context = {'country_code': None}

            logger.info('========== Finished getting global configurations ==========')
            return render(request, 'country/country_code.html', context)

        except Exception as e:
            logger.info('Exception:')
            logger.info(e)
            logger.info('========== Finished getting global configurations ==========')
            context = {'country_code': None}

            return render(request, 'country/country_code.html', context)

    @staticmethod
    def post(request, *args, **kwargs):

        country_code = request.POST.get('country_code')
        logger.info('========== Start adding country code ==========')
        logger.info('Username: {}'.format(request.user.username))

        params = {
            'value': "" + country_code,
        }

        try:
            url = settings.ADD_COUNTRY_CODE_URL
            logger.info('Request URL: {}'.format(url))

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

            client_id = settings.CLIENTID
            logger.info('client id ' + client_id)

            data_log = copy.deepcopy(params)
            data_log['client_secret'] = ''
            logger.info("Expected country code {}".format(data_log))

            start_date = time.time()
            response = requests.put(url, headers=headers, json=params, verify=settings.CERT)
            done = time.time()
            logger.info("Response time is {} sec.".format(done - start_date))

            response_json = response.json()
            status = response_json['status']

            logger.info("Response Code is {}".format(status['code']))
            logger.info("Response JSON is {}".format(response_json))

            if response.status_code == 200:

                if status['code'] == "success":
                    logger.info("Country code was added.")
                    logger.info('========== Finish adding country code ==========')
                    return HttpResponse(status=200, content=response)
                else:
                    logger.info("Error adding country code {}".format(country_code))
                    logger.info('========== Finish adding country code ==========')
                    return HttpResponse(status=500, content=response)

            else:
                logger.info('Error code: {}'.format(response.status_code))
                return HttpResponse(status=response.status_code, content=response)

        except Exception as e:
            logger.info('Exception: ')
            logger.info(e)
            logger.info('========== Finish adding country code ==========')
            return HttpResponse(status=500, content=e)
