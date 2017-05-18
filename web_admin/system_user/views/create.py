import copy
import logging
import time

import requests
from django.conf import settings
from django.shortcuts import redirect, render
from django.views import View

from authentications.utils import get_auth_header
from authentications.apps import InvalidAccessToken
from django.contrib import messages

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
        }

        try:
            url = settings.SYSTEM_USER_CREATE_URL

            logger.info("URL: {}".format(url))
            data_log = copy.deepcopy(params)
            data_log.pop('password', None)
            logger.info("Request: {}".format(data_log))

            start_date = time.time()
            response = requests.post(url, headers=get_auth_header(request.user),
                                     json=params, verify=settings.CERT)
            done = time.time()
            logger.info("Response time is {} sec.".format(done - start_date))
            logger.info("Response Code: {}".format(response.status_code))
            logger.info("Response Content: {}".format(response.content))
            response_json = response.json()
            status = response_json.get('status', {})
            code = status.get('code', '')
            if (code == "access_token_expire") or (code== 'access_token_not_found'):
                message = status.get('message', 'Something went wrong.')
                raise InvalidAccessToken(message)
            

            if response.status_code == 200:
                response_json = response.json()
                status = response_json['status']

                if status['code'] == "success":
                    logger.info("system user was created.")
                    logger.info('========== Finish creating new system user ==========')
                    messages.add_message(request, messages.SUCCESS, 'Added data successfully')
                    return redirect('system_user:search')
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
