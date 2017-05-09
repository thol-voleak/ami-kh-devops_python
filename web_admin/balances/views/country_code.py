import copy
import logging
import time
import requests
from authentications.apps import InvalidAccessToken
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from authentications.apps import InvalidAccessToken

from authentications.utils import get_auth_header

logger = logging.getLogger(__name__)


class CountryCode(View):
    @staticmethod
    def get(request, *args, **kwargs):
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
        logger.info('Response Content: {}'.format(response.text))

        status = response_json.get('status', {})
        if not isinstance(status, dict):
            status = {}
        code = status.get('code', '')
        message = status.get('message', 'Something went wrong.')
        if code == "success":
            logger.info("Global configuration was fetched.")
            context = {'country_code': response_json['data']['country']}
        else:
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                logger.info("{} for {} username".format(message, request.user))
                raise InvalidAccessToken(message)
            context = {'country_code': None}

        logger.info('========== Finished getting global configurations ==========')
        return render(request, 'country/country_code.html', context)

    @staticmethod
    def post(request, *args, **kwargs):

        country_code = request.POST.get('country_code')
        logger.info('========== Start adding country code ==========')
        logger.info('Username: {}'.format(request.user.username))

        params = {
            'value': "" + country_code,
        }

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
        logger.info("Response JSON is {}".format(response.text))
        response_json = response.json()

        status = response_json.get('status', {})
        if not isinstance(status, dict):
            status = {}
        code = status.get('code', '')
        message = status.get('message', 'Something went wrong.')
        if code == "success":
            logger.info("Country code was added.")
            logger.info('========== Finish adding country code ==========')
            return HttpResponse(status=200, content=response)
        else:
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                logger.info("{} for {} username".format(message, request.user))
                raise InvalidAccessToken(message)
            return HttpResponse(status=response.status_code, content=response)
