import requests
import logging
import time

from django.views.generic.base import TemplateView
from django.conf import settings
from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header
from django.shortcuts import redirect, render
from web_admin.utils import format_date_time
from django.contrib import messages

logger = logging.getLogger(__name__)


class ListCommandView(TemplateView):
    template_name = "command/list.html"

    def post(self, request, *args, **kwargs):
        logger.info('========== Start adding service command ==========')

        service_id = kwargs['service_id']
        command_id = request.POST.get('command_id')

        data = {
            'service_id': service_id,
            'command_id': command_id,
        }

        data, success = self._add_service_command(data)
        logger.info('========== Finish adding service command ==========')
        if success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Added command successfully'
            )

        return redirect('services:fee_tier_list', service_id=service_id, command_id=command_id, service_command_id=0)

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)

        return self._headers

    def _add_service_command(self, data):
        logger.info("Updating service command by user {}".format(self.request.user.username))

        url = settings.SERVICE_COMMAND_ADD_URL

        logger.info('Updating service command request url: {}'.format(url))
        logger.info('Updating service command request body: {}'.format(data))
        response = requests.post(url, headers=self._get_headers(), json=data, verify=settings.CERT)
        logger.info("Updating service command response code {}".format(response.status_code))
        logger.info("Updating service command response content {}".format(response.content))

        if response.status_code == 200:
            json_data = response.json()
            return json_data.get('data'), True
        else:
            return None, False

    def get_context_data(self, **kwargs):
        context = super(ListCommandView, self).get_context_data(**kwargs)
        service_id = context['service_id']

        logger.info('========== Start get Services Command List ==========')
        data, service_name = self.get_commands_list(service_id)
        refined_data = format_date_time(data)
        logger.info('========== Finished get Services Command List ==========')

        logger.info('========== Start get Command List ==========')
        commands_dd_list = self._get_commands_dd_list();
        logger.info('========== Finished get Command List ==========')

        context['data'] = refined_data
        context['service_name'] = service_name
        context['command_id'] = commands_dd_list[0]["command_id"]
        context['commands_dd_list'] = commands_dd_list

        return context

    def get_commands_list(self, service_id):
        logger.info("Getting command list by user {}".format(self.request.user.username))
        headers = get_auth_header(self.request.user)

        url = settings.COMMAND_LIST_BY_SERVICE_URL.format(service_id)

        logger.info("Getting command list from backend with {} url".format(url))
        auth_request = requests.get(url, headers=headers, verify=settings.CERT)

        json_data = auth_request.json()

        detail_url = settings.SERVICE_DETAIL_URL.format(service_id)
        service_detail = requests.get(detail_url, headers=headers, verify=settings.CERT)
        service_detail = service_detail.json().get("data")
        data = json_data.get('data')
        service_name = service_detail["service_name"]

        if auth_request.status_code == 200:
            if data is not None:
                logger.info('Command count: {}'.format(len(data)))
                return data, service_name

        if json_data["status"]["code"] == "access_token_expire":
            logger.info("{} for {} username".format(json_data["status"]["message"], self.request.user))
            raise InvalidAccessToken(json_data["status"]["message"])
        else:
            raise Exception("{}".format(json_data["status"]["message"]))

    def _get_commands_dd_list(self):

        logger.info("Getting command list by {} user id".format(self.request.user.username))
        headers = get_auth_header(self.request.user)

        url = settings.COMMAND_LIST_URL

        logger.info("Getting command list from backend with {} url".format(url))
        start_date = time.time()
        auth_request = requests.get(url, headers=headers, verify=settings.CERT)
        end_date = time.time()
        logger.info("Getting command list response time is {} sec.".format(end_date - start_date))

        json_data = auth_request.json()
        data = json_data.get('data')
        if auth_request.status_code == 200:
            if (data is not None) and (len(data) > 0):
                logger.info('Service command count: {}'.format(len(data)))
                return data

        if json_data["status"]["code"] == "access_token_expire":
            logger.info("{} for {} username".format(json_data["status"]["message"], self.request.user))
            raise InvalidAccessToken(json_data["status"]["message"])
        else:
            raise Exception("{}".format(json_data["status"]["message"]))
