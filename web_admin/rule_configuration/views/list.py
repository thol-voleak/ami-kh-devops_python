from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from datetime import datetime
from web_admin.api_logger import API_Logger
from django.shortcuts import render
import logging
from braces.views import GroupRequiredMixin
from authentications.apps import InvalidAccessToken
from web_admin.api_settings import SEARCH_RULE, GET_RULE
from django.contrib import messages


logger = logging.getLogger(__name__)


class RuleList(GroupRequiredMixin, TemplateView, GetHeaderMixin):

    template_name = "rule_configuration/list.html"
    group_required = "CAN_VIEW_RULE_LIST"
    login_url = 'web:permission_denied'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(RuleList, self).dispatch(request, *args, **kwargs)

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def post(self, request, *args, **kwargs):
        campaign_name = request.POST.get('campaign_name')
        campaign_id = request.POST.get('campaign_id')
        status = request.POST.get('status')
        start_date = request.POST.get('dtp_from')
        to_date = request.POST.get('dtp_to')

        body = {}
        # if campaign_name:
        #     body['campaign_name'] = campaign_name
        if campaign_id:
            body['rule_id'] = int(campaign_id)
        if (status == 'True'):
            body['is_active'] = True
        if (status == 'False'):
            body['is_active'] = False

        if start_date:
            new_from_created_timestamp = datetime.strptime(start_date, "%Y-%m-%d")
            new_from_created_timestamp = new_from_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['start_active_timestamp'] = new_from_created_timestamp

        if to_date:
            new_to_created_timestamp = datetime.strptime(to_date, "%Y-%m-%d")
            new_to_created_timestamp = new_to_created_timestamp.replace(hour=23, minute=59, second=59)
            new_to_created_timestamp = new_to_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            body['end_active_timestamp'] = new_to_created_timestamp

        self.logger.info('========== Start searching Rule ==========')


        data = self._search_for_rule(body)
        is_permission_detail = check_permissions_by_user(self.request.user, 'CAN_VIEW_RULE_DETAILS  ')
        is_permission_update_status = check_permissions_by_user(self.request.user, 'CAN_ENABLE_DISABLE_RULE')
        for i in data:
            i['is_permission_detail'] = is_permission_detail
            i['is_permission_update_status'] = is_permission_update_status
        #data = self.format_data(data)
        status_list = self._get_status_list()
        permissions = {}
        permissions['CAN_VIEW_RULE_DETAILS'] = check_permissions_by_user(self.request.user,'CAN_VIEW_RULE_DETAILS')
        permissions['CAN_CREATE_RULE'] = check_permissions_by_user(self.request.user, 'CAN_CREATE_RULE')

        context = {
            'data': data,
            'status_list': status_list,
            'campaign_name': campaign_name,
            'campaign_id': campaign_id,
            'selected_status': status,
            'start_date': start_date,
            'to_date': to_date,
            'permissions': permissions,
        }

        self.logger.info('========== Finished searching Rule ==========')

        return render(request, self.template_name, context)

    def get(self, request, *args, **kwargs):
        data = self.get_rule()
        is_permission_detail = check_permissions_by_user(self.request.user, 'CAN_VIEW_RULE_DETAILS')
        is_permission_update_status = check_permissions_by_user(self.request.user, 'CAN_ENABLE_DISABLE_RULE')
        
        for i in data:
            i['is_permission_detail'] = is_permission_detail
            i['is_permission_update_status'] = is_permission_update_status

        status_list = self._get_status_list()
        permissions = {}
        permissions['CAN_VIEW_RULE_DETAILS'] = check_permissions_by_user(self.request.user, 'CAN_VIEW_RULE_DETAILS')
        permissions['CAN_CREATE_RULE'] = check_permissions_by_user(self.request.user, 'CAN_CREATE_RULE')
        context = {
            'data': data,
            'status_list': status_list,
            'permissions': permissions,
        }
        return render(request, self.template_name, context)

    def get_rule(self):
        url = GET_RULE
        self.logger.info('========== Start get rule list ==========')
        is_success, status_code, data = RestFulClient.get(url=url, headers=self._get_headers(), loggers=self.logger)
        if is_success:
            if data is None or data == "":
                data = []
        else:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format(data))
                raise InvalidAccessToken(data)
            data = []
        self.logger.info('Response_content_count: {}'.format(len(data)))
        self.logger.info('========== Finish get rule list ==========')
        return data

    def _search_for_rule(self, body):
        is_success, status_code, status_message, data = RestFulClient.post(url=SEARCH_RULE,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=body)

        API_Logger.post_logging(loggers=self.logger, params=body, response=data,
                                status_code=status_code, is_getting_list=True)

        if not is_success:
            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )
            data = []
        return data

    def format_data(self, data):
        return data

    def _get_status_list(self):
        return [
            {"name": "All", "value": ""},
            {"name": "Active", "value": "True"},
            {"name": "Inactive", "value": "False"},
        ]
