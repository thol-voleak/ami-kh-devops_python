import logging
import time

import requests
from django.conf import settings
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView

from authentications.utils import get_auth_header
from authentications.apps import InvalidAccessToken

logger = logging.getLogger(__name__)

class SystemUserUpdateForm(TemplateView):
    template_name = "system_user/system_user_update.html"

    def get_context_data(self, **kwargs):
        try:
            logger.info('========== Start getting system user detail ==========')

            context = super(SystemUserUpdateForm, self).get_context_data(**kwargs)
            system_user_id = context['systemUserId']

            return self._get_system_user_detail(system_user_id)

        except:
            context = {'system_user_info': {}}
            return context

    def post(self, request, *args, **kwargs):
        logger.info('========== Start updating system user ==========')
        system_user_id = kwargs['systemUserId']
        url = settings.UPDATE_SYSTEM_USER_URL.format(system_user_id)
        logger.info("URL: {}".format(url))

        username = request.POST.get('username_input')
        firstname = request.POST.get('firstname_input')
        lastname = request.POST.get('lastname_input')
        email = request.POST.get('email_input')

        params = {
            "username": username,
            "firstname": firstname,
            "lastname": lastname,
            "email": email,
        }
        logger.info('PUT Request: {}'.format(params))

        try:
            start_time = time.time()

            response = requests.put(url, headers=get_auth_header(request.user),
                                    json=params, verify=settings.CERT)

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
                    logger.info("System User was updated.")
                    logger.info('========== Finished updating System User ==========')
                    request.session['system_user_update_msg'] = 'Updated system user successfully'
                    return redirect('system_user:system-user-detail', systemUserId=(system_user_id))
                else:
                    logger.info("Error Updating System User {}".format(system_user_id))
                    context = {'system_user_info': params}
                    logger.info('========== Finish updating system user ==========')
                    return render(request, 'system_user/system_user_update.html', context)
            else:
                logger.info("Error Updating System User {}".format(system_user_id))
                logger.info("Status code {}".format(response.status_code))
                context = {'system_user_info': params}
                logger.info('========== Finish updating system user ==========')
                return render(request, 'system_user/system_user_update.html', context)

        except Exception as e:
            logger.info(e)
            logger.info('system_user.id: ' + system_user_id)
            context = {'system_user_info': params}
            logger.info('========== Finish updating System User ==========')
            return render(request, 'system_user/system_user_update.html', context)

    def _get_system_user_detail(self, system_user_id):

        url = settings.SYSTEM_USER_DETAIL_URL.format(system_user_id)
        logger.info("Username: {}".format(self.request.user.username))
        logger.info('Getting system user detail from backend')
        logger.info("URL: {}".format(url))
        start_date = time.time()
        response = requests.get(url, headers=get_auth_header(self.request.user),
                                verify=settings.CERT)
        logger.info("Response Content: {}".format(response.content))
        done = time.time()
        logger.info("Response time is {} sec.".format(done - start_date))
        logger.info("Received data with response status is {}".format(response.status_code))

        response_json = response.json()
        status = response_json.get('status', {})
        code = status.get('code', '')
        if (code == "access_token_expire") or (code== 'access_token_not_found'):
            message = status.get('message', 'Something went wrong.')
            raise InvalidAccessToken(message)
        if response_json['status']['code'] == "success":
            data = response_json.get('data')
            context = {'system_user_info': data}
            logger.info('========== Finished getting system user detail ==========')
            return context
        else:
            logger.info("Error Getting System User Detail.")
            context = {'system_user_info': response_json.get('data')}
            logger.info('========== Finished getting system user detail ==========')
            return context

