from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.conf import settings
from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header

import requests, time
import logging

logger = logging.getLogger(__name__)

class ServiceGroupUpdateForm(TemplateView):
    template_name = "service_group/update.html"

    def get_context_data(self, **kwargs):
        try:
            logger.info('========== Start getting service group detail ==========')

            context = super(ServiceGroupUpdateForm, self).get_context_data(**kwargs)
            service_group_id = context['ServiceGroupId']

            return self._get_service_group_detail(service_group_id)

        except:
            context = {'service_group_info': {}}
            return context

    def post(self, request, *args, **kwargs):
        logger.info('========== Start updating service group ==========')
        service_group_id = kwargs['ServiceGroupId']
        url = settings.DOMAIN_NAMES + settings.SERVICE_GROUP_UPDATE_URL.format(service_group_id)
        logger.info("URL: {}".format(url))

        name = request.POST.get('service_group_name')
        description = request.POST.get('description')

        params = {
            "service_group_name": name,
            "description": description,
        }
        logger.info('PUT Request: {}'.format(params))


        headers = get_auth_header(self.request.user)

        start_time = time.time()

        response = requests.put(url, headers=headers, json=params, verify=settings.CERT)

        logger.info("Response: {}".format(response.content))
        end_time = time.time()
        logger.info("Response time is {} sec.".format(end_time - start_time))
        logger.info("Response Code is {}".format(response.status_code))

        response_json = response.json()
        status = response_json.get('status', {})
        # if not isinstance(status, dict):
        #     status = {}
        code = status.get('code', '')

        message = status.get('message', 'Something went wrong.')
        if code == "success":
            logger.info("Service Group was updated.")
            logger.info('========== Finished updating Service Group ==========')
            request.session['service_group_update_msg'] = 'Updated service group successfully'
            return redirect('service_group:service_group_detail', ServiceGroupId=(service_group_id))
        else:
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)

            logger.info("Error Updating Service Group {}".format(service_group_id))
            context = {'service_group_info': params}
            logger.info('========== Finish updating service group ==========')
            return render(request, 'service_group/update.html', context)


    def _get_service_group_detail(self, service_group_id):

        url = settings.DOMAIN_NAMES + settings.SERVICE_GROUP_DETAIL_URL.format(service_group_id)

        headers = get_auth_header(self.request.user)

        logger.info("Username: {}".format(self.request.user))
        logger.info('Getting service group detail from backend')
        logger.info("URL: {}".format(url))
        start_date = time.time()

        response = requests.get(url, headers=headers, verify=settings.CERT)

        logger.info("Response Content: {}".format(response.content))
        done = time.time()
        logger.info("Response time is {} sec.".format(done - start_date))
        logger.info("Received data with response status is {}".format(response.status_code))

        response_json = response.json()
        status = response_json.get('status', {})
        # if not isinstance(status, dict):
        #     status = {}
        code = status.get('code', '')

        message = status.get('message', 'Something went wrong.')
        if code == "success":
            data = response_json.get('data')
            context = {'service_group_info': data}
            logger.info('========== Finished getting service group detail ==========')
            return context
        else:
            if (code == "access_token_expire") or (code == 'access_token_not_found'):
                logger.info("{} for {} username".format(message, self.request.user))
                raise InvalidAccessToken(message)

            logger.info("Error Getting System User Detail.")
            context = {'service_group_info': response_json.get('data')}
            logger.info('========== Finished getting service group detail ==========')
            return context

