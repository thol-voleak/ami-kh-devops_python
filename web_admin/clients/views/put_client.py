import time
import requests

from django.http import HttpResponse
from authentications.utils import get_auth_header
from authentications.apps import InvalidAccessToken
from django.conf import settings


def put_client(request, url, title, logger, client_id):
    logger.info('========== Start {} client =========='.format(title))
    params = {
        'status': title,
    }

    try:
        logger.info('API-Path: {}'.format(url))
        logger.info("Params: {} ".format(params))
        start = time.time()
        response = requests.put(url, headers=get_auth_header(request.user),
                                json=params, verify=settings.CERT)
        finish = time.time()
        logger.info("Response_time: {} sec.".format(finish - start))

        response_json = response.json()
        status = response_json.get('status', {})
        code = status.get('code', '')

        if code in ['access_token_expire', 'access_token_not_found', 'invalid_access_token']:
            message = status.get('message', 'Something went wrong.')
            logger.info("{} for {} username".format(message, request.user))
            raise InvalidAccessToken(message)

        logger.info('Response_code: {}'.format(response.status_code))
        logger.info('Response_content: {}'.format(response.text))
        logger.info('Response_time: {}'.format(finish - start))

        if code == "success":
            status = 200
        else:
            logger.info("Error suspending Client {}".format(client_id))
            status = 500
        logger.info('========== Finish {} client =========='.format(title))
        return HttpResponse(status=status, content=response)

    except Exception as e:
        logger.info(e)
        return HttpResponse(status=500, content=e)