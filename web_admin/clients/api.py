import json
import logging
import time
import requests
from django.conf import settings
from django.http import JsonResponse
from authentications.utils import get_auth_header
from web_admin import api_settings
from django.contrib import messages

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
        logger.info('Response_code: {}'.format(response.status_code))
        logger.info('Response_content: {}'.format(response.text))
        logger.info('Response_time: {}'.format(finish - start))
        response_json = response.json()
        status = response_json.get('status', {})

        code = 0
        message = status.get('message', 'Something went wrong.')
        if status['code'] in ['access_token_expire', 'access_token_not_found', 'invalid_access_token']:
            logger.info("{} for {} username".format(message, request.user))
            messages.add_message(request, messages.INFO, str('session_is_expired'))
            code = 1
            return JsonResponse({"status": code, "msg": message})

        if status['code'] == "success":
            code = 2
        else:
            code = 3
        logger.info('========== Finish regenerate client secret ==========')
        return JsonResponse({"status": code, "msg": message})

    def delete_client_by_id(request, client_id):
        logger.info("========== Start delete client id ==========")
        if request.method == "POST":
            url = settings.DOMAIN_NAMES + api_settings.DELETE_CLIENT_URL.format(client_id)
            logger.info('API-Path: {}'.format(url))
            start = time.time()
            response = requests.delete(url, headers=get_auth_header(request.user),
                                       verify=settings.CERT)
            done = time.time()
            logger.info('Response_code: {}'.format(response.status_code))
            logger.info('Response_content: {}'.format(response.text))
            logger.info('Response_time: {}'.format(done - start))
            response_json = response.json()
            status = response_json.get('status', {})

            code = 0
            message = status.get('message', 'Something went wrong.')
            if status['code'] in ['access_token_expire', 'access_token_not_found', 'invalid_access_token']:
                logger.info("{} for {} username".format(message, request.user))
                messages.add_message(request, messages.INFO, str('session_is_expired'))
                code = 1
                return JsonResponse({"status": code, "msg": message})

            if status['code'] == "success":
                code = 2
            else:
                code = 3
            logger.info('========== Finish delete client id ==========')
            return JsonResponse({"status": code, "msg": message})
