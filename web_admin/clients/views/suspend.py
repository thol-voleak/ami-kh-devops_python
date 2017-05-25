import copy
import logging
import time

import requests
from django.conf import settings
from web_admin import api_settings
from django.http import HttpResponse

from authentications.utils import get_auth_header
from authentications.apps import InvalidAccessToken

logger = logging.getLogger(__name__)


def suspend(request, client_id):
    logger.info('========== Start suspending client ==========')
    logger.info('The Client to be suspended {} client id.'.format(client_id))

    params = {
        'status': 'suspend',
    }

    try:
        url = settings.DOMAIN_NAMES + api_settings.SUSPEND_CLIENT_URL.format(client_id)
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
        code = status.get('code', '')
        if (code == "access_token_expire") or (code== 'access_token_not_found'):
            message = status.get('message', 'Something went wrong.')
            raise InvalidAccessToken(message)

        logger.info("Response Code is {}".format(status['code']))

        if response.status_code == 200:
            if status['code'] == "success":
                logger.info("Client was suspended.")
                logger.info('========== Finish suspending client ==========')
                return HttpResponse(status=200, content=response)
            else:
                logger.info("Error suspending Client {}".format(client_id))
                logger.info('========== Finish suspending client ==========')
                return HttpResponse(status=500, content=response)
        else:
            logger.info("Error suspending Client {}".format(client_id))
            logger.info("Status code {}".format(response.status_code))

            logger.info('========== Finish suspending client ==========')
            return HttpResponse(status=response.status_code, content=response)

    except Exception as e:
        logger.info(e)
        logger.info('client_id: ' + client_id)
        logger.info('========== Finish suspending client ==========')
        return HttpResponse(status=500, content=e)
