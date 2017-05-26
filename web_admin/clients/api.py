import json
import logging
import time
import requests
from django.conf import settings
from django.http import HttpResponse
from authentications.utils import get_auth_header
from authentications.apps import InvalidAccessToken
from web_admin import api_settings


logger = logging.getLogger(__name__)


class ClientApi():
    def regenerate(request, client_id):
        logger.info('========== Start regenerating client secret ==========')

        url = settings.DOMAIN_NAMES + api_settings.REGENERATE_CLIENT_SECRET_URL.format(client_id)
        logger.info('API-Path: {}'.format(url))
        start = time.time()
        response = requests.post(url, headers=get_auth_header(request.user),
                                 verify=settings.CERT)
        finish = time.time()
        logger.info("Response time: {} sec.".format(finish - start))
        response_json = response.json()
        status = response_json['status']

        if status['code'] in ['access_token_expire', 'access_token_not_found', 'invalid_access_token']:
            message = status.get('message', 'Something went wrong.')
            logger.info("{} for {} username".format(message, request.user))
            raise InvalidAccessToken(message)

        if status['code'] == "success":
            status = 200
        else:
            status = 500
        logger.info('========== Finish regenerate client secret ==========')
        return HttpResponse(status=status, content=response)

    def delete_client_by_id(request, client_id):
        logger.info("========== Start delete client id ==========")
        if request.method == "POST":
            url = settings.DOMAIN_NAMES + api_settings.DELETE_CLIENT_URL.format(client_id)
            logger.info('API-Path: {}'.format(url))
            start = time.time()
            response = requests.delete(url, headers=get_auth_header(request.user),
                                       verify=settings.CERT)
            done = time.time()
            logger.info("Response time: {} sec.".format(done - start))
            logger.info("Response content: {}".format(response.content))

            json_response = response.json()
            logger.info("========== Finished deleted client id ==========")
            if response.status_code == 200:
                return HttpResponse(json.dumps(json_response["status"]), content_type="application/json")

            raise Exception("{}".format(json_response["status"]["message"]))
