from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.api_logger import API_Logger
from django.contrib import messages
from web_admin import api_settings, setup_logger, RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin
from braces.views import GroupRequiredMixin
from web_admin import api_settings

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

        success, status_code, status_message, data = self.create_action(rule_id, mechanic_id, params)

        #API_Logger.post_logging(loggers=self.logger, params=params, response=data, status_code=status_code)
        self.logger.info('========== Finish create action ==========')
        if success:
            messages.success(request, "Rule ID {} is updated successfully".format(rule_id))
            return redirect('rule_configuration:rule_detail', rule_id=rule_id)
        elif status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
            self.logger.info("{}".format(status_message))
            raise InvalidAccessToken(status_message)

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
        success, status_code, message, data = RestFulClient.post(
                url = api_settings.CREATE_ACTION.format(rule_id=rule_id, mechanic_id=mechanic_id),
                headers=self._get_headers(),
                loggers=self.logger,
                params=params)
        return success, status_code, message, data






