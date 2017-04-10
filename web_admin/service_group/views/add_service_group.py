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

        try:
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

            json_data = response.json()
            if response.status_code == 200:
                status = json_data.get('status')
                if status['code'] == 'success':
                    logger.info("Service Group was created.")
                    logger.info('========== Finish creating Service Group ==========')
                    request.session['add_service_group_msg'] = 'Added data successfully'
                    service_group_id = json_data['data']['service_group_id']
                    return redirect('service_group:service_group_detail', ServiceGroupId=(service_group_id))

            if json_data["status"]["code"] == "access_token_expire":
                logger.info("{} for {} username".format(json_data["status"]["message"], request.user))
                logger.info('========== Finish creating Service Group ==========')
                raise InvalidAccessToken(json_data["status"]["message"])
            else:
                logger.info('========== Finish creating Service Group ==========')
                raise Exception("{}".format(json_data["status"]["message"]))

        except Exception as e:
            logger.info(e)
            service_group_info = {
                "service_group_name": name,
                "description": description
            }
            context = {'service_group_info': service_group_info}
            logger.info('========== Finish creating Service Group ==========')
            return render(request, 'service_group/add_service_group.html', context)
