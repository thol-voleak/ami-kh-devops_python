import logging

from django.views.generic.base import TemplateView
from web_admin.restful_client import RestFulClient
from authentications.apps import InvalidAccessToken
from web_admin.get_header_mixins import GetHeaderMixin
from django.shortcuts import render
from web_admin import api_settings, setup_logger
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user

logger = logging.getLogger(__name__)


class ReportConfigurationList(TemplateView, GetHeaderMixin):
    template_name = "report-configuration/list.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ReportConfigurationList, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        self.logger.info('========== Start getting report configurations ==========')


        self.logger.info('========== Start get service whitelist list ==========')
        whitelist_services = self.get_whitelist_services()
        self.logger.info('========== Finish get service whitelist list ==========')

        self.logger.info('========== Start get service group list ==========')
        service_group_list = self.get_service_group_list()
        self.logger.info('========== Finish get service group list ==========')

        self.logger.info('========== Start get service list  ==========')
        service_list = self.get_service_list()
        self.logger.info('========== Finish get service list ==========')

        self.logger.info('========== Finish getting report configurations ==========')

        shown_service_group_list = []
        for service_group in service_group_list:
            shown_service_list = []
            checked_count= 0
            for service in service_list:
                if service_group['service_group_id'] == service['service_group_id']:
                    if service['is_deleted']:
                        for whitelist in whitelist_services:
                            if service['service_id'] == whitelist['service_id'] and not whitelist['is_deleted']:
                                service['is_checked'] = True
                                checked_count += 1
                                shown_service_list.append(service)
                                break
                    else:
                        service['is_checked'] = False
                        for whitelist in whitelist_services:
                            if service['service_id'] == whitelist['service_id'] and not whitelist['is_deleted']:
                                checked_count += 1
                                service['is_checked'] = True
                                break
                        shown_service_list.append(service)
            if len(shown_service_list) == 0:
                continue
            service_group['service_list'] = list(shown_service_list)
            service_group['is_checked'] = False
            if checked_count == len(shown_service_list):
                service_group['is_checked'] = True
            shown_service_group_list.append(service_group)

        return render(request, self.template_name, {'service_group_list': shown_service_group_list})

    def get_whitelist_services(self):
        is_success, status_code, data = RestFulClient.get(url=api_settings.GET_WHITELIST_REPORT, headers=self._get_headers(), loggers=self.logger)
        if is_success:
            if data is None or data == "":
                data = []
            elif data['services']:
                data = data['services']
            else:
                data = []
        else:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format(data))
                raise InvalidAccessToken(data)
            data = []
        self.logger.info('Response_content_count: {}'.format(len(data)))
        return data

    def get_service_group_list(self):
        url = api_settings.SERVICE_GROUP_LIST_URL
        is_success, status_code, data = RestFulClient.get(url, headers=self._get_headers(), loggers=self.logger)

        if is_success:
            if data is None or data == "":
                data = []
        else:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format(data))
                raise InvalidAccessToken(data)
            data = []
        self.logger.info('Response_content_count: {}'.format(len(data)))
        return data

    def get_service_list(self):
        url = api_settings.SERVICE_LIST_URL
        is_success, status_code, data = RestFulClient.get(url, headers=self._get_headers(), loggers=self.logger)

        if is_success:
            if data is None or data == "":
                data = []
        else:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format(data))
                raise InvalidAccessToken(data)
            data = []
        self.logger.info('Response_content_count: {}'.format(len(data)))
        return data




