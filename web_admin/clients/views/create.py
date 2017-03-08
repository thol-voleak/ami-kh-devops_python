from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.base import TemplateView
from django.conf import settings
import requests, random, string, time
from django.contrib.auth.models import User
from authentications.models import Authentications

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

    def post(self, request, *args, **kwargs):
        # import pdb;pdb.set_trace()
        try:

            logger.info('========== Start creating new client ==========')

            url = settings.CREATE_CLIENT_URL

            correlation_id = ''.join(
                random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

            client_id = request.POST.get('client_id')
            client_secret = request.POST.get('client_secret')

            client_info = {
                "client_id": request.POST.get('client_id'),
                "client_secret": request.POST.get('client_secret'),
                "scope": "read write",
                "client_name": request.POST.get('client_name'),
                "authorized_grant_types": request.POST.get('authorized_grant_types'),
                "web_server_redirect_uri": request.POST.get('web_server_redirect_uri'),
                "authorities": "",
                "redirect_uri": request.POST.get('redirect_uri'),
                "additional_information": "",
                "autoapprove": "",
                "access_token_validity": request.POST.get('access_token_validity'),
                "refresh_token_validity": request.POST.get('refresh_token_validity'),
            }

            logger.info("{} params".format(client_info))

            auth = Authentications.objects.get(user=request.user)
            access_token = auth.access_token

            headers = {
                'content-type': 'application/json',
                'correlation-id': correlation_id,
                'client_id': settings.CLIENTID,
                'client_secret': settings.CLIENTSECRET,
                'Authorization': 'Bearer ' + access_token,
            }


            logger.info('Calling API gateway')
            # import ipdb;ipdb.set_trace()

            start_date = time.time()
            import pdb;pdb.set_trace()
            response = requests.post(url, params=client_info, headers=headers, verify=False)
            response_json = response.json()
            # import ipdb;ipdb.set_trace()
            done = time.time()
            logger.info("Response time is {} sec.".format(done-start_date))
            logger.info("Create client response is {}".format(response.status_code))
            logger.info("Create client response is XXX {}".format(response))

            logger.info("Created Client Successfully.")
            status = response_json['status']
            if status['code'] == "success":
                logger.info('Redirecting to Clients List')
                return redirect('client-list')
            else:
                logger.info("Error Creating Client !!!")
                context = {'client_info': client_info,
                           'error_msg': response_json['status'].message}

                return render(request, 'clients/create_client_form.html', context)

            # if response.status_code == 200:
            #     logger.info("Created Client Successfully.")
            #     status = response_json['status']
            #     if status['code'] == "Success":
            #         logger.info('Redirecting to Clients List')
            #         return redirect('client-list')
            #     else:
            #         logger.info("Error Creating Client !!!")
            #         context = {'client_info': client_info,
            #                    'error_msg': response_json['status'].message}
            #
            #         return render(request, 'clients/create_client_form.html', context)
            # else:
            #     logger.info("Error Creating Client !!!")
            #     context = {'client_info': client_info,
            #                'error_msg': 'Something went wrong!'}
            #
            #     return render(request, 'clients/create_client_form.html', context)

        except Exception as e:
            logger.info('========== Finish creating new client ==========')
            logger.info(e)
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



    def _generate_client_id(self):
        client_id = ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(32))
        return client_id

    def _generate_client_secret(self):
        client_secret = ''.join(
            random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(64))
        return client_secret