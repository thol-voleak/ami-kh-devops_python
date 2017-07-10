import logging
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.base import TemplateView
from web_admin import api_settings
from multiprocessing.pool import ThreadPool
from web_admin.restful_methods import RESTfulMethods
from web_admin.utils import setup_logger
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

IS_SUCCESS = {
    True: 'Success',
    False: 'Failed',
}


class PartnerFileList(TemplateView, RESTfulMethods):
    template_name = "reconcile/partner_file_list.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(PartnerFileList, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = {}

        # Set first load default time for Context
        default_end_date = datetime.today().strftime("%Y-%m-%d")
        default_start_date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

        service_list, get_service_status = self._get_service('-1')

        choices, success = self._get_service_group_and_currency_choices()
        context ={'from_created_timestamp' : default_start_date,
                  'to_created_timestamp' : default_end_date,
                  'service_get_url': api_settings.GET_SERVICE_URL,
                  'choices' : choices}

        if get_service_status == True:
            context['service_list'] = service_list

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start searching partner file list ==========')
        choices, success = self._get_service_group_and_currency_choices()

        is_on_us = request.POST.get('on_off_us_id')
        service_group = request.POST.get('service_group_id')
        service_id = request.POST.get('service_id')
        agent_id = request.POST.get('partner_id')
        currency = request.POST.get('currency_id')
        reconcile_status = request.POST.get('reconcile_status_id')
        from_created_timestamp = request.POST.get('from_created_timestamp')
        to_created_timestamp = request.POST.get('to_created_timestamp')

        params = {}

        is_on_us_id = int(is_on_us)
        service_group_id = int(service_group)
        reconcile_status_id = int(reconcile_status)

        if is_on_us_id >= 0:
            params['is_on_us'] = (is_on_us_id == 1)

        service_list, get_service_status  = self._get_service(service_group)
        if get_service_status == True:
            for service_in in service_list:
                if service_in['service_id'] == int(service_id):
                    params['service_name'] = service_in['service_name']
                    break

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

        data = self._search_file_list(params)

        context = {'is_on_us' : is_on_us_id,
                   'service_group_id' : service_group_id,
                   'agent_id' : agent_id,
                   'currency' : currency,
                   'status_id' : reconcile_status_id,
                   'from_created_timestamp' : from_created_timestamp,
                   'to_created_timestamp' : to_created_timestamp,
                   'choices' : choices,
                   'file_list' : data,
                   'service_id':int(service_id),
                   }

        if get_service_status == True:
            context['service_list'] = service_list
        self.logger.info(
            "========== Finish searching partner file list ==========")

        return render(request, self.template_name, context)

    def _search_file_list(self, params):
        api_path = api_settings.SEARCH_RECONCILE_PARTNER_FILE_LIST

        data, success = self._post_method(
            api_path=api_path,
            func_description="Search Partner File List",
            logger=logger,
            params=params
        )
        self.logger.info("data={}".format(data))
        return data

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
        url = api_settings.SERVICE_GROUP_LIST_URL
        return self._get_method(url, "services group list", logger, True)

    def _get_service_group_and_currency_choices(self):
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
        return None, False

    def _get_service(self, service_group_id):
        if service_group_id == '-1':
            url = api_settings.GET_ALL_SERVICE_URL
            return self._get_method(url, "services", logger, True)
        url = api_settings.GET_SERVICE_URL
        url = url.replace("{service_group_id}", service_group_id)
        return self._get_method(url, "services", logger, True)



