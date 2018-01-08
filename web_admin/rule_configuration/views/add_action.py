from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.api_logger import API_Logger
from web_admin import api_settings, setup_logger, RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin
from braces.views import GroupRequiredMixin
import time
import requests
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from authentications.utils import get_auth_header
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from datetime import datetime

import logging

logger = logging.getLogger(__name__)

class AddRuleAction(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    group_required = "CAN_CREATE_RULE"
    login_url = 'web:permission_denied'
    raise_exception = False

    template_name = 'rule_configuration/add_action.html'
    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AddRuleAction, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(AddRuleAction, self).get_context_data(**kwargs)
        context['action_types'] = self.get_action_types_list()
        context['data_types'] = self.get_data_types_list()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = super(AddRuleAction, self).get_context_data(**kwargs)
        rule_id = context['rule_id']
        mechanic_id = context['mechanic_id']
        self.logger.info('========== Start create action ==========')
        action_type_id = request.POST.get('action_type')
        send_to = request.POST.get('send_to')
        key_name = request.POST.get('key_name')
        key_value_type = request.POST.get('key_value_type')
        key_value = request.POST.get('key_value')
        body ={
            'action_type_id':action_type_id,
            'send_to':send_to,
            'key_name':key_name,
            'key_value_type':key_value_type,
            'key_value':key_value
        }
        if key_value_type == 'timestamp':
            timestamp = datetime.strptime(key_value, "%Y-%m-%dT%H:%M")
            key_value = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
        params = {
            'action_type_id':action_type_id,
            'data':
            [
                {
                    'key_name':key_name,
                    'key_value_type':key_value_type,
                    'key_value':key_value
                    }
                ]
        }
        if action_type_id == '2':
            params['data'].append({
                'key_name':'notification_url',
                'key_value_type':'text',
                'key_value':send_to
            })

        self.logger.info("param is : {}".format(params))
        result = self.create_action(rule_id, mechanic_id, params)

        self.logger.info('========== Finish create action ==========')

        return  result


    def get_action_types_list(self):
        self.logger.info('========== Start get action type list ==========')
        success, status_code, data  = RestFulClient.get(url=api_settings.GET_ACTION_TYPE, loggers=self.logger, headers=self._get_headers())
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                                status_code=status_code)
        self.logger.info('========== finish get action type list ==========')
        return data

    def get_data_types_list(self):
        self.logger.info('========== Start get data type list ==========')
        success, status_code, data  = RestFulClient.get(url=api_settings.GET_DATA_TYPE, loggers=self.logger, headers=self._get_headers())
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                            status_code=status_code)
        self.logger.info('========== finish get data type list ==========')
        return data

    def create_action(self, rule_id, mechanic_id, params):
        #rule_id = 99999
        api_path = api_settings.CREATE_ACTION.format(rule_id=rule_id, mechanic_id=mechanic_id)
        url = settings.DOMAIN_NAMES + api_path

        timeout = settings.GLOBAL_TIMEOUT


        logger.info('API-Path: {path}'.format(path=api_path))

        start = time.time()
        try:
            response = requests.post(url, headers=get_auth_header(self.request.user), json=params, verify=settings.CERT,
                                     timeout=timeout)
        except requests.exceptions.Timeout:
            return JsonResponse({'status': 'timeout'})
        done = time.time()
        logger.info('Response_code: {}'.format(response.status_code))
        logger.info('Response_content: {}'.format(response.text))
        logger.info('Response_time: {}'.format(done - start))
        response_json = response.json()
        status = response_json.get('status', {})

        code = 0
        message = status.get('message', 'Something went wrong.')
        if status['code'] in ['access_token_expire', 'authentication_fail', 'invalid_access_token']:
            logger.info("{} for {} username".format(message, self.request.user))
            messages.add_message(self.request, messages.INFO,
                                 str('Your login credentials have expired. Please login again.'))
            code = 1
            return JsonResponse({"status": code, "msg": message})

        if status['code'] == "success":
            code = 2
            messages.success(self.request, "Rule ID {} is updated successfully".format(rule_id))
        else:
            code = 3

        return JsonResponse({"status": code, "msg": message, "data": response_json.get('data', {})})






