import requests, random, string, time
import copy

from django.conf import settings
from django.http import HttpResponse

from authentications.models import Authentications
from authentications.apps import InvalidAccessToken

import logging

logger = logging.getLogger(__name__)


def suspend(request, client_id):
    logger.info('========== Start suspending client ==========')
    logger.info('The Client to be suspended {} client id.'.format(client_id))

    params = {
        'status': 'suspend',
    }

    try:
        url = settings.SUSPEND_CLIENT_URL.format(client_id)
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