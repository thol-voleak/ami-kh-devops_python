import logging

from django.contrib import messages
from django.views.generic.base import TemplateView
from web_admin.restful_client import RestFulClient
from authentications.apps import InvalidAccessToken
from web_admin.get_header_mixins import GetHeaderMixin
from django.shortcuts import render, redirect
from web_admin.api_logger import API_Logger
from web_admin import api_settings, setup_logger
from datetime import datetime
from web_admin.utils import convert_string_to_date_time
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user

logger = logging.getLogger(__name__)

class ReportConfigurationList(TemplateView, GetHeaderMixin):
    template_name = "report-configuration/list.html"
    logger = logger

    OPERAND_VALUES = ['default', 'fee', 'amount', 'bonus', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o']
    OPERAND_KEYS = ['tpv','fee','commission']

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ReportConfigurationList, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context={}

        self.logger.info('========== Start getting report configurations ==========')

        self.logger.info('========== Start get report type list ==========')
        report_types, is_success = self.get_report_type_list()
        self.logger.info('========== Finish get report type list ==========')

        shown_service_group_list = []
        checked_service_arr = []

        if report_types is not None:
            first_report_type_id = report_types[0]['id']

        selected_report_type = request.GET.get("report_type_id", first_report_type_id)

        if is_success:
            if selected_report_type:
                self.logger.info('========== Start get service whitelist list ==========')
                whitelist_services = self.get_whitelist_services(selected_report_type)
                self.logger.info('========== Finish get service whitelist list ==========')
                formula = self.get_formula(selected_report_type)
            self.logger.info('========== Start get service group list ==========')
            service_group_list = self.get_service_group_list()
            self.logger.info('========== Finish get service group list ==========')

            self.logger.info('========== Start get service list  ==========')
            service_list = self.get_service_list()
            self.logger.info('========== Finish get service list ==========')

            self.logger.info('========== Finish getting report configurations ==========')

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
                service_group['is_indeterminate'] = False
                if checked_count == len(shown_service_list):
                    service_group['is_checked'] = True
                if 0 < checked_count < len(shown_service_list):
                    service_group['is_indeterminate'] = True
                shown_service_group_list.append(service_group)

            formula_operands = {}
            for key in formula.keys():
                if key in self.OPERAND_KEYS and formula[key] is not None:
                    formula_operands[key] = formula[key]
            formula['effective_date'] = datetime.strptime(formula['effective_timestamp'],'%Y-%m-%dT%H:%M:%SZ').strftime("%Y-%m-%d");
            formula['operands'] = formula_operands;
            context.update({'service_group_list': shown_service_group_list, 'checked_service_arr' : checked_service_arr,
                                                'report_types': report_types,
                                                'selected_report_type': int(selected_report_type),'formula':formula,'operand_values':self.OPERAND_VALUES})

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        report_type_id = request.POST.get('report_type_id')
        checked_service_arr = request.POST.getlist('checked_list')
        new_checked_list = request.POST.getlist('service')
        effective_date = request.POST.get('effective_date')
        tpv = request.POST.get('tpv')
        fee = request.POST.get('fee')
        commission = request.POST.get('commission')
        effective_timestamp = convert_string_to_date_time(effective_date, "00:00:00")

        params = {'tpv': tpv,
                  'fee': fee,
                  'commission': commission,
                  'effective_timestamp': effective_timestamp }

        deleted_service_arr = []
        added_service_arr = []

        for origin_service in checked_service_arr:
            if origin_service not in new_checked_list:
                deleted_service_arr.append(int(origin_service))
        for new_service in new_checked_list:
            if new_service not in checked_service_arr:
                added_service_arr.append(int(new_service))

        is_add_success = self.add_service(report_type_id, added_service_arr)
        is_delete_success = self.delete_service(report_type_id, deleted_service_arr)
        is_update_formula_success = self.update_formula(report_type_id, params)

        if is_add_success and is_delete_success and is_update_formula_success:
            messages.add_message(request, messages.SUCCESS, 'Change has been saved')
        else:
            messages.add_message(request, messages.ERROR, 'There was an error occurred, please try submitting again')
        return redirect('report_configuration:report_configuration')

    def get_whitelist_services(self, report_type_id):
        url = api_settings.GET_WHITELIST_REPORT.format(report_type_id=report_type_id)
        is_success, status_code, data = RestFulClient.get(url=url, headers=self._get_headers(), loggers=self.logger)
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

    def get_formula(self, report_type_id):
        self.logger.info('========== Start get formula list of Report type Id {} =========='.format(report_type_id));
        url = api_settings.GET_FORMULA_REPORT.format(report_type_id=report_type_id)
        is_success, status_code, data = RestFulClient.get(url=url, headers=self._get_headers(), loggers=self.logger)
        if  not is_success:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format(data))
                raise InvalidAccessToken(data)
            data = {}
        self.logger.info('========== Finish get formula ==========');
        return data

    def get_report_type_list(self):
        is_success, status_code, data = RestFulClient.get(api_settings.GET_REPORT_TYPE_LIST,
                                                          headers=self._get_headers(),
                                                          loggers=self.logger)
        if is_success:
            report_types = data.get('report_types', None)
        else:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format(data))
                raise InvalidAccessToken(data)
            report_types = []
        self.logger.info('Response_content_count: {}'.format(len(data)))
        return report_types, is_success

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

    def add_service(self, report_type_id, service_id_list):
        self.logger.info('========== Start add service to whitelist ==========')
        url = api_settings.ADD_SERVICE.format(report_type_id=report_type_id)
        params = {'service_ids': service_id_list}

        is_success, status_code, status_message, data = RestFulClient.post(url,
                                                                            headers=self._get_headers(),
                                                                            params=params, loggers=self.logger)
        API_Logger.post_logging(loggers=self.logger, params=params, response=data,
                                status_code=status_code)
        self.logger.info('========== Finish add service to whitelist  ==========')
        return is_success

    def delete_service(self, report_type_id, service_id_list):
        self.logger.info('========== Start delete service from whitelist ==========')
        url = api_settings.DELETE_SERVICE.format(report_type_id=report_type_id)
        params = {'service_ids': service_id_list}

        is_success, status_code, data = RestFulClient.delete(url,
                                                            headers=self._get_headers(),
                                                            params=params, loggers=self.logger)
        self.logger.info("Params: {} ".format(params))
        API_Logger.delete_logging(loggers=self.logger, status_code=status_code)
        self.logger.info('========== Finish delete service from whitelist ==========')
        return is_success

    def update_formula(self, report_type_id, params):
        self.logger.info('========== Start update payment report formula ==========')
        url = api_settings.UPDATE_REPORT_FORMULA.format(report_type_id=report_type_id)
        is_success, status_code, status_message, data = RestFulClient.put(url,
                                                                           headers=self._get_headers(),
                                                                           params=params, loggers=self.logger)
        API_Logger.put_logging(loggers=self.logger, params=params, response=data,
                                status_code=status_code)
        self.logger.info('========== Finish update payment report formula  ==========')
        return is_success






