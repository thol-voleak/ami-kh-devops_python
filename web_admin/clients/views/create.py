from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.base import TemplateView
from django.conf import settings
import requests, random, string

from authentications.models import *

import logging, datetime

logger = logging.getLogger(__name__)


class ClientCreate(View):
    def get(self, request, *args, **kwargs):
        # import pdb;pdb.set_trace()
        client_id = self._generate_client_id()
        client_secret = self._generate_client_secret()
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

    def post(self, request, args, *kwargs):
        try:
            logger.info('========== Start creating new client ==========')

            url = settings.CREATE_CLIENT_URL

            correlation_id = ''.join(
                random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

            client_id = request.POST.get('client_id')
            client_secret = request.POST.get('client_secret')

            client_info = {
                "client_id": client_id,
                "client_secret": client_secret,
                "client_name": request.POST.get('client_name'),
                "scope": request.POST.get('scope'),
                "authorized_grant_types": request.POST.get('authorized_grant_types'),
                "redirect_uri": request.POST.get('redirect_uri'),
                "access_token_validity": request.POST.get('access_token_validity'),
                "refresh_token_validity": request.POST.get('refresh_token_validity'),
            }

            headers = {
                'content-type': 'application/json', # 'application/x-www-form-urlencoded',
                'correlation-id': correlation_id,
            }

            logger.info('Calling API gateway')
            # import ipdb;ipdb.set_trace()

            start_date = time.time()
            response = requests.post(url, params=client_info, headers=headers)
            response_json = response.json()
            # import ipdb;ipdb.set_trace()
            done = time.time()
            logger.info("Response time is {} sec.".format(done-start_date))
            logger.info("Create client response is {}".format(response.status_code))
            logger.info("Create client response is XXX {}".format(response))

            if response.status_code == 200:
                logger.info("Created Client Successfully.")
                if response_json['status'].code == "Success":
                    logger.info('Redirecting to Clients List')
                    return redirect('client-list')
                else:
                    logger.info("Error Creating Client !!!")
                    context = {'client_info': client_info,
                               'error_msg': response_json['status'].message}

                    return render(request, 'clients/create_client_form.html', context)
            else:
                logger.info("Error Creating Client !!!")
                context = {'client_info': client_info,
                           'error_msg': 'Something went wrong!'}

                return render(request, 'clients/create_client_form.html', context)

        except:
            logger.info('========== Finish creating new client ==========')
            return None


    def _generate_client_id(self):
        client_id = ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(32))
        return client_id

    def _generate_client_secret(self):
        client_secret = ''.join(
            random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(64))
        return client_secret