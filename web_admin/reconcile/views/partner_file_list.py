import logging

import requests
from authentications.utils import get_correlation_id_from_username
from django.shortcuts import render
from django.views.generic.base import TemplateView
from web_admin import api_settings
from multiprocessing.pool import ThreadPool
from web_admin.restful_methods_reconcile import RESTfulReconcileMethods
from web_admin.utils import setup_logger
from datetime import datetime, timedelta
from web_admin.utils import calculate_page_range_from_page_info

logger = logging.getLogger(__name__)

IS_SUCCESS = {
    True: 'Success',
    False: 'Failed',
}


class PartnerFileList(TemplateView, RESTfulReconcileMethods):
    template_name = "reconcile/partner_file_list.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(PartnerFileList, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        # Set first load default time for Context
        default_end_date = datetime.today().strftime("%Y-%m-%d")
        default_start_date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

        context = {'from_created_timestamp': default_start_date,
                   'to_created_timestamp': default_end_date }

        currencies, success = self._get_currency_choices()
        if success:
            context.update({'currencies': currencies})

        services_list, service_groups, service_group_id, success = self._get_service_group_and_services_list(-1)
        if success:
            context.update({'service_list': services_list,
                            'service_groups': service_groups,
                            'service_group_id': service_group_id})
        else:
            context.update({'partner_file_list_error_msg': 'Fail to get service group, please refresh the page or contact technical support'})

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start searching partner file list ==========')
        context = super(PartnerFileList, self).get_context_data(**kwargs)

        opening_page_index = request.POST.get('current_page_index')
        is_on_us = request.POST.get('on_off_us_id')
        service_group_id = request.POST.get('service_group_id')
        service_name = request.POST.get('service_name')
        agent_id = request.POST.get('partner_id')
        currency = request.POST.get('currency_id')
        reconcile_status = request.POST.get('reconcile_status_id')
        from_created_timestamp = request.POST.get('from_created_timestamp')
        to_created_timestamp = request.POST.get('to_created_timestamp')

        params = {}
        params['opening_page_index'] = opening_page_index

        is_on_us_id = int(is_on_us)
        reconcile_status_id = int(reconcile_status)

        if is_on_us_id >= 0:
            params['is_on_us'] = (is_on_us_id == 1)

        if service_name != '':
            if service_name == None:
                params['service_name'] = ''
            else:
                params['service_name'] = service_name

        if agent_id != '':
            params['agent_id'] = int(agent_id)

        if currency != '':
            params['currency'] = currency

        if reconcile_status_id >= 0:
            params['status_id'] = reconcile_status_id

        if from_created_timestamp is not '':
            new_from_created_timestamp = datetime.strptime(from_created_timestamp, "%Y-%m-%d")
            new_from_created_timestamp = new_from_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            params['from_last_updated_timestamp'] = new_from_created_timestamp

        if to_created_timestamp is not '':
            new_to_created_timestamp = datetime.strptime(to_created_timestamp, "%Y-%m-%d")
            new_to_created_timestamp = new_to_created_timestamp.replace(hour=23, minute=59, second=59)
            new_to_created_timestamp = new_to_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            params['to_last_updated_timestamp'] = new_to_created_timestamp

        currencies, success = self._get_currency_choices()
        if success is True:
            context.update({'currencies': currencies})

        services_list, service_groups, service_group_id, success = self._get_service_group_and_services_list(
            service_group_id)
        if success is True:
            context.update({'service_list': services_list,
                            'service_groups': service_groups,
                            'service_group_id': service_group_id})
        else:
            context.update({'partner_file_list_error_msg': 'Fail to get service group, please refresh the page or contact technical support'})
            params.pop('service_name','')

        try:
            data, page, status_code = self._search_file_list(params)
            if status_code == 500:
                self.logger.error('Search fail, please try again or contact technical support')
                context.update({'partner_file_list_error_msg': 'Search fail, please try again or contact technical support'})
            else:
                context.update({'file_list': data, 'paginator': page, 'page_range': calculate_page_range_from_page_info(page)})

        except requests.Timeout:
            self.logger.error('Search partner file list request timeout')
            context.update({'partner_file_list_error_msg': 'Search timeout, please try again or contact technical support'})

        context.update({'is_on_us': is_on_us_id,
                        'agent_id': agent_id,
                        'currency': currency,
                        'status_id': reconcile_status_id,
                        'from_created_timestamp': from_created_timestamp,
                        'to_created_timestamp': to_created_timestamp,
                        'selected_service': service_name})

        self.logger.info("========== Finish searching partner file list ==========")

        return render(request, self.template_name, context)

    def _search_file_list(self, params):
        self.logger.info('========== Start Searching Partner File List ==========')
        api_path = api_settings.SEARCH_RECONCILE_PARTNER_FILE_LIST
        response_json, success = self._post_method(
            api_path=api_path,
            func_description="Search Partner File List",
            logger=logger,
            params=params,
            only_return_data=False
        )
        self.logger.info("data={}".format(response_json.get('data')))
        self.logger.info('========== Finish Searching Partner File List ==========')
        return response_json.get('data'), response_json.get('page'), response_json.get("status_code")

    def _get_currency_choices(self):
        self.logger.info('========== Start Getting Currency Choices ==========')
        url = api_settings.GET_ALL_CURRENCY_URL
        data, success = self._get_method(url, "currency choice", logger)

        if success:
            value = data.get('value', '')
            if isinstance(value, str):
                currency_list = map(lambda x: x.split('|'), value.split(','))
            else:
                currency_list = []
            result = currency_list, True
        else:
            result = [], False
        self.logger.info('========== Finish Getting Currency Choices ==========')
        return result

    def _get_service_group_choices(self):
        self.logger.info('========== Start Getting Service Groups ==========')
        url = api_settings.SERVICE_GROUP_LIST_URL
        service_group_list = self._get_method(url, "services group list", logger, True)
        self.logger.info('========== Finish Getting Service Groups ==========')
        return service_group_list

    def _get_service_group_and_currency_choices(self):
        self.logger.info('========== Start Getting Service_Groups and Currencies Choices ==========')
        pool = ThreadPool(processes=1)
        async_result = pool.apply_async(self._get_currency_choices)
        self.logger.info('========== Start Getting Service Group Choices ==========')
        service_groups, success_service = self._get_service_group_choices()
        self.logger.info('========== Finish Getting Service Group Choices ==========')
        currencies, success_currency = async_result.get()
        if success_currency and success_service:
            return {
                       'currencies': currencies,
                       'service_groups': service_groups,
                   }, True
        self.logger.info('========== Finish Getting Service_Groups and Currencies Choices ==========')
        return None, False

    def _get_service(self, service_group_id):
        self.logger.info('========== Start Getting Service List ==========')
        if service_group_id == -1:
            data, success = self._get_method(api_settings.GET_ALL_SERVICE_URL, "Get all service", logger)
        else:
            data, success = self._get_method(
                api_settings.GET_SERVICE_BY_SERVICE_GROUP_URL.format(service_group_id=service_group_id),
                "Get services by service group",
                logger)
        self.logger.info('========== Finish Getting Service List ==========')
        return data, success

    def _get_service_group_and_services_list(self, service_group_id):
        if service_group_id is not None:
            service_groups, success = self._get_service_group_choices()
            if success:
                service_group_id = int(service_group_id)
                services_list, success = self._get_service(service_group_id)
                if success:
                    return  services_list, service_groups, service_group_id, True
                else:
                    logger.error("Get Services List Error")
                    return None, None, None, False
            else:
                logger.error("Get Service Group Error")
                return None, None, None, False
        else:
            logger.error("No service group")
            return None, None, None, False



