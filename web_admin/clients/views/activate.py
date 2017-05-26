import requests
import time
import copy

from django.conf import settings
from web_admin import api_settings
from django.http import HttpResponse
from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header

import logging

logger = logging.getLogger(__name__)


def activate(request, client_id):
    logger.info('========== Start activating client ==========')
    logger.info('The Client to be activated {} client id.'.format(client_id))

    params = {
        'status': 'active',
    }

    try:
        url = settings.DOMAIN_NAMES + api_settings.ACTIVATE_CLIENT_URL.format(client_id)
        data_log = copy.deepcopy(params)
        data_log['client_secret'] = ''
        logger.info("Expected client status {}".format(data_log))

        start_date = time.time()
        response = requests.put(url, headers=get_auth_header(request.user),
                                json=params, verify=settings.CERT)
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

        if response_json["status"]["message"] == "Invalid access token":
            raise InvalidAccessToken(response_json["status"]["message"])

    except Exception as e:
        logger.info(e)
        logger.info('client_id: ' + client_id)
        logger.info('========== Finish activating client ==========')
        return HttpResponse(status=500, content=e)
