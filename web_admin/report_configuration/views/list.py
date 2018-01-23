import logging

from django.contrib import messages
from django.views.generic.base import TemplateView
from web_admin.restful_client import RestFulClient
from authentications.apps import InvalidAccessToken
from web_admin.get_header_mixins import GetHeaderMixin
from django.shortcuts import render, redirect
from web_admin.api_logger import API_Logger
from web_admin import api_settings, setup_logger
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user

logger = logging.getLogger(__name__)
checked_service_arr = []

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
        global checked_service_arr
        checked_service_arr = []
        for service_group in service_group_list:
            shown_service_list = []
            checked_count= 0
            for service in service_list:
                if service_group['service_group_id'] == service['service_group_id']:
                    if service['is_deleted']:
                        for whitelist in whitelist_services:
                            if service['service_id'] == whitelist['service_id'] and not whitelist['is_deleted']:
                                service['is_checked'] = True
                                if service['service_id'] not in checked_service_arr:
                                    checked_service_arr.append(service['service_id'])
                                checked_count += 1
                                shown_service_list.append(service)
                                break
                    else:
                        service['is_checked'] = False
                        for whitelist in whitelist_services:
                            if service['service_id'] == whitelist['service_id'] and not whitelist['is_deleted']:
                                checked_count += 1
                                service['is_checked'] = True
                                if service['service_id'] not in checked_service_arr:
                                    checked_service_arr.append(service['service_id'])
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

    def post(self, request, *args, **kwargs):
        global checked_service_arr
        new_checked_list = request.POST.getlist('service')
        new_service_list = []
        for i in new_checked_list:
            new_service_list.append(int(i))
        deleted_service_arr = []
        added_service_arr = []
        for origon_service in checked_service_arr:
            if origon_service not in new_service_list:
                deleted_service_arr.append(origon_service)
        for new_service in new_service_list:
            if new_service not in checked_service_arr:
                added_service_arr.append(new_service)

        is_add_sucess = self.add_service(added_service_arr)
        if is_add_sucess:
            is_delete_success = self.delete_service(deleted_service_arr)
            if is_delete_success:
                messages.add_message(request, messages.SUCCESS, 'Change has been saved')
                return redirect('report_configuration:report_configuration')
            else:
                messages.add_message(request, messages.ERROR, 'There was an error occurred, please try submitting again')
                return redirect('report_configuration:report_configuration')
        else:
            messages.add_message(request, messages.ERROR, 'There was an error occurred, please try submitting again')
            return redirect('report_configuration:report_configuration')


        return redirect('report_configuration:report_configuration')

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

    def add_service(self, service_id_list):
        url = api_settings.ADD_SERVICE
        params = {'service_ids': service_id_list}
        print(params)

        is_success, status_code, status_message, data = RestFulClient.post(url, 
                                                                            headers=self._get_headers(), 
                                                                            params=params, loggers=self.logger)
        API_Logger.post_logging(loggers=self.logger, params=params, response=data,
                                status_code=status_code)
        return is_success

    def delete_service(self, service_id_list):
        url = api_settings.DELETE_SERVICE
        params = {'service_ids': service_id_list}
        print(params)

        is_success, status_code, data = RestFulClient.delete(url, 
                                                            headers=self._get_headers(), 
                                                            params=params, loggers=self.logger)
        API_Logger.delete_logging(loggers=self.logger, status_code=status_code)

        return is_success






