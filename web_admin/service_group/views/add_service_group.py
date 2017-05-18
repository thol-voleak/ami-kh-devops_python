from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header

import requests,time
import logging

logger = logging.getLogger(__name__)


class ServiceGroupCreate(View):
    @staticmethod
    def get(request, *args, **kwargs):
        service_group_info = {
            "name": None,
            "description": None,
        }
        context = {'service_group_info': service_group_info}
        return render(request, 'service_group/add_service_group.html', context)

    @staticmethod
    def post(request, *args, **kwargs):
        logger.info('========== Start creating Service Group ==========')
        name = request.POST.get('name')
        description = request.POST.get('description')

        url = settings.ADD_SERVICE_GROUP_URL
        headers = get_auth_header(request.user)

        params = {
            "service_group_name": name,
            "description": description
        }
        logger.info('username {} creating service group with url: {}'.format(request.user.username, url))
        logger.info('username {} creating service group with params: {}'.format(request.user.username, params))

        start_date = time.time()
        response = requests.post(url, headers=headers, json=params, verify=settings.CERT)
        done = time.time()
        logger.info("Response time is {} sec.".format(done - start_date))
        logger.info("username {} Received response code is {}".format(request.user.username, response.status_code))
        logger.info("username {} Received response data is {}".format(request.user.username, response.content))

        response_json = response.json()
        status = response_json.get('status', {})
        # if not isinstance(status, dict):
        #     status = {}
        code = status.get('code', '')
        message = status.get('message', 'Something went wrong.')
        if code == "success":
            logger.info("Service Group was created.")
            logger.info('========== Finish creating Service Group ==========')
            request.session['add_service_group_msg'] = 'Added data successfully'
            service_group_id = response_json['data']['service_group_id']
            return redirect('service_group:service_group_detail', ServiceGroupId=(service_group_id))

        else:
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                logger.info("{} for {} username".format(message, request.user))
                raise InvalidAccessToken(message)

            service_group_info = {
                "service_group_name": name,
                "description": description
            }
            context = {'service_group_info': service_group_info}
            logger.info('========== Finish creating Service Group ==========')
            return render(request, 'service_group/add_service_group.html', context)

