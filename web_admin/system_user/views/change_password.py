from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.conf import settings
from authentications.utils import get_auth_header
from authentications.apps import InvalidAccessToken
from web_admin import api_settings
import requests, time
import logging
from django.contrib import messages

logger = logging.getLogger(__name__)

class SystemUserChangePassword(TemplateView):
    template_name = "system_user/system_user_change_password.html"

    def get_context_data(self, **kwargs):
        try:

            context = super(SystemUserChangePassword, self).get_context_data(**kwargs)
            system_user_id = context['systemUserId']

            system_user_info = {
                "id": system_user_id,
                "password": None,
            }
            context = {'system_user_info': system_user_info}
            return context

        except:
            context = {'system_user_info': {}}
            return context

    def post(self, request, *args, **kwargs):
        logger.info('========== Start changing system user password ==========')
        system_user_id = kwargs['systemUserId']
        url = settings.DOMAIN_NAMES + api_settings.SYSTEM_USER_CHANGE_PASSWORD_URL.format(system_user_id)
        logger.info("URL: {}".format(url))

        password = request.POST.get('newpassword')

        params = {"password": password}
        logger.info("Request: new password is ******")

        headers = get_auth_header(self.request.user)

        start_time = time.time()

        response = requests.put(url, headers=headers, json=params, verify=settings.CERT)

        logger.info("Response: {}".format(response.content))
        end_time = time.time()
        logger.info("Response time is {} sec.".format(end_time - start_time))

        response_json = response.json()
        status = response_json['status']
        code = status.get('code', '')
        if (code == "access_token_expire") or (code== 'access_token_not_found'):
            message = status.get('message', 'Something went wrong.')
            raise InvalidAccessToken(message)

        logger.info("Response Code is {}".format(status['code']))

        if response.status_code == 200:
            if status['code'] == "success":
                logger.info("System User password was changed.")
                logger.info('========== Finished changing System User Password ==========')
                messages.add_message(request, messages.SUCCESS, 'Password has been changed successfully')
                return redirect('system_user:system-user-list')
            else:
                logger.info("Error changing password of System User {}".format(system_user_id))
                context = {'system_user_info': params}
                logger.info('========== Finish changing system user password ==========')
                return render(request, 'system_user/system_user_change_password.html', context)
        else:
            logger.info("Error Changing password of System User {}".format(system_user_id))
            logger.info("Status code {}".format(response.status_code))
            context = {'system_user_info': params}
            logger.info('========== Finish changing system user password ==========')
            return render(request, 'system_user/system_user_change_password.html', context)
