import copy
import logging
import time

import requests
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from authentications.utils import get_auth_header

logger = logging.getLogger(__name__)


class CountryCode(View):
    @staticmethod
    def get(request, *args, **kwargs):

        try:
            logger.info('========== Start getting global configurations ==========')

            url = settings.GLOBAL_CONFIGURATIONS_URL

            logger.info('Username: {}'.format(request.user.username))
            logger.info('Request URL: {}'.format(url))

            logger.info('Sending request to API-Gateway')
            start_date = time.time()
            response = requests.get(url, headers=get_auth_header(request.user),
                                    verify=settings.CERT)
            done = time.time()

            response_json = response.json()
            context = None

            logger.info("Response time is {} sec.".format(done - start_date))
            logger.info("Received data with response status is {}".format(response.status_code))
            logger.info('Response Content: {}'.format(response_json))

            if response.status_code == 200:

                if response_json['status']['code'] == "success":
                    logger.info("Global configuration was fetched.")
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

            data_log = copy.deepcopy(params)
            data_log['client_secret'] = ''
            logger.info("Expected country code {}".format(data_log))

            start_date = time.time()
            response = requests.put(url, headers=get_auth_header(request.user),
                                    json=params, verify=settings.CERT)
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
