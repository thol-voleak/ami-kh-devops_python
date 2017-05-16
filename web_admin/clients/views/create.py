import logging
import random
import string
import time

import requests
from django.conf import settings
from django.shortcuts import redirect, render
from django.views import View

from authentications.utils import get_auth_header
from authentications.apps import InvalidAccessToken

logger = logging.getLogger(__name__)


class ClientCreate(View):
    @staticmethod
    def get(request, *args, **kwargs):
        client_id = _generate_client_id()
        client_secret = _generate_client_secret()
        client_info = {
            "client_id": client_id,
            "client_secret": client_secret,
            "authorized_grant_types": None,
            "access_token_validity": None,
            "refresh_token_validity": None,
            "authorization_code_validity": None
        }
        context = {'client_info': client_info,
                   'error_msg': None}

        return render(request, 'clients/create_client_form.html', context)

    @staticmethod
    def post(request, *args, **kwargs):
        logger.info('========== Start creating new client ==========')
        client_id = request.POST.get('client_id')
        client_secret = request.POST.get('client_secret')

        try:
            url = settings.CREATE_CLIENT_URL

            params = {
                "client_id": client_id,
                "client_secret": client_secret,
                "client_name": request.POST.get('client_name'),
                "scope": "",
                "authorized_grant_types": request.POST.get('authorized_grant_types'),
                "web_server_redirect_uri": request.POST.get('web_server_redirect_uri'),
                "authorities": "",
                "access_token_validity": request.POST.get('access_token_validity'),
                "refresh_token_validity": request.POST.get('refresh_token_validity'),
                "authorization_code_validity": request.POST.get('authorization_code_validity')
            }

            start_date = time.time()
            response = requests.post(url, headers=get_auth_header(request.user),
                                     json=params, verify=settings.CERT)
            done = time.time()
            logger.info("Response time is {} sec.".format(done - start_date))

            response_json = response.json()

            status = response_json['status']            
            code = status.get('code', '')
            if (code == "access_token_expire") or (code== 'access_token_not_found'):
                message = status.get('message', 'Something went wrong.')
                raise InvalidAccessToken(message)
            if status['code'] == "success":
                logger.info("Client was created.")
                logger.info('========== Finish create new client ==========')
                return redirect('clients:client-list')
            else:
                logger.info("Error Creating Client.")
                context = {'client_info': params,
                           'error_msg': response_json['status']['message']}
                logger.info('========== Finish create new client ==========')
                return render(request, 'clients/create_client_form.html', context)

        except Exception as e:
            logger.info(e)
            client_info = {
                "client_id": client_id,
                "client_secret": client_secret,
                "authorized_grant_types": None,
                "access_token_validity": None,
                "refresh_token_validity": None,
            }
            context = {'client_info': client_info, 'error_msg': None}
            logger.info('========== Finish create new client ==========')
            return render(request, 'clients/create_client_form.html', context)


def _generate_client_id():
    client_id = ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(32))
    return client_id


def _generate_client_secret():
    client_secret = ''.join(
        random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(64))
    return client_secret
