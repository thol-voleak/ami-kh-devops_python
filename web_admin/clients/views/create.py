from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
import requests, random, string, time
from authentications.models import Authentications

from authentications.models import *

import logging

logger = logging.getLogger(__name__)


class ClientCreate(View):
    @staticmethod
    def get(request, *args, **kwargs):
        # import pdb;pdb.set_trace()
        client_id = _generate_client_id()
        client_secret = _generate_client_secret()
        client_info = {
            "client_id": client_id,
            "client_secret": client_secret,
            "authorized_grant_types": None,
            "access_token_validity": None,
            "refresh_token_validity": None,
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
            auth = Authentications.objects.get(user=request.user)
            access_token = auth.access_token

            correlation_id = ''.join(
                random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

            headers = {
                'content-type': 'application/json',
                'correlation-id': correlation_id,
                'client_id': settings.CLIENTID,
                'client_secret': settings.CLIENTSECRET,
                'Authorization': access_token,
            }

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
                "additional_information": "",
                "resource_ids": "",
                "authorities": "",
                "autoapprove": ""
            }

            start_date = time.time()
            response = requests.post(url, headers=headers, json=params, verify=False)
            done = time.time()
            logger.info("Response time is {} sec.".format(done - start_date))
            response_json = response.json()
            # logger.info("Create client response is {}".format(response.status_code))
            # logger.info("Create client response is XXX {}".format(response))
            #
            # logger.info("Created Client Successfully.")
            status = response_json['status']
            if status['code'] == "success":
                logger.info('Redirecting to Clients List')
                return redirect('clients:client-list')
            else:
                logger.info("Error Creating Client !!!")
                context = {'client_info': params,
                           'error_msg': response_json['status'].message}

                return render(request, 'clients/create_client_form.html', context)

        except Exception as e:
            logger.info('========== Finish creating new client ==========')
            logger.info(e)
            client_info = {
                "client_id": client_id,
                "client_secret": client_secret,
                "authorized_grant_types": None,
                "access_token_validity": None,
                "refresh_token_validity": None,
            }
            context = {'client_info': client_info,
                       'error_msg': None}

            return render(request, 'clients/create_client_form.html', context)


def _generate_client_id():
    client_id = ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(32))
    return client_id


def _generate_client_secret():
    client_secret = ''.join(
        random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(64))
    return client_secret
