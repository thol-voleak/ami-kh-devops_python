from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
import requests, random, string, time
from authentications.apps import InvalidAccessToken
from authentications.models import *
import copy

import logging

logger = logging.getLogger(__name__)


class SystemUserCreate(View):
    @staticmethod
    def get(request, *args, **kwargs):
        logger.info('========== Fetch form for creating new system user ==========')
        system_user_info = {
            "username": None,
            "firstname": None,
            "lastname": None,
            "email": None,
            "password": None,
            "confirm_password": None,
        }
        context = {'system_user_info': system_user_info,
                   'error_msg': None}
        logger.info('========== Finish fetching form for creating new system user ==========')
        return render(request, 'system_user/create_system_user.html', context)

    @staticmethod
    def post(request, *args, **kwargs):
        logger.info('========== Start creating new system user ==========')
        logger.info('Username: {}'.format(request.user.username))
        params = {
            "username": request.POST.get('username'),
            "firstname": request.POST.get('firstname'),
            "lastname": request.POST.get('lastname'),
            "email": request.POST.get('email'),
            "password": request.POST.get('password'),
            "confirm_password": request.POST.get('confirm_password'),
        }

        try:
            url = settings.SYSTEM_USER_CREATE_URL
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
                'Authorization': 'Bearer ' + access_token,
            }

            logger.info("URL: {}".format(url))
            data_log = copy.deepcopy(params)
            data_log.pop('password', None)
            data_log.pop('confirm_password', None)
            logger.info("Request: {}".format(data_log))

            start_date = time.time()
            response = requests.post(url, headers=headers, json=params, verify=False)
            done = time.time()
            logger.info("Response time is {} sec.".format(done - start_date))
            logger.info("Response Code: ".format(response.status_code))
            logger.info("Response Content: ".format(response.content))

            if response.status_code == 200:
                response_json = response.json()
                status = response_json['status']

                if status['code'] == "success":
                    logger.info("system user was created.")
                    logger.info('========== Finish creating new system user ==========')
                    request.session['system_user_create_msg'] = 'Added data successfully'
                    return redirect('system_user:system-user-list')
                else:
                    logger.info("Error Creating system user.")
                    logger.info('{}'.format(status['message']))
                    context = {'system_user_info': params,
                               'error_msg': status['message']}
                    logger.info('========== Finish creating new system user ==========')
                    return render(request, 'system_user/create_system_user.html', context)
            else:
                logger.info("Error Creating system user.")
                context = {'system_user_info': params,
                           'error_msg': "Error occurred."}
                logger.info('========== Finish creating new system user ==========')
                return render(request, 'system_user/create_system_user.html', context)

        except Exception as e:
            logger.info('Exception:')
            logger.info(e)
            context = {'system_user_info': params,
                       'error_msg': "Exception occurred."}
            logger.info('========== Finish creating new system user ==========')
            return render(request, 'system_user/create_system_user.html', context)