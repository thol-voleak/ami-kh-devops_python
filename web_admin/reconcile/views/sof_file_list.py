import logging

from datetime import datetime, timedelta

import requests
from django.shortcuts import render
from django.views.generic.base import TemplateView
from web_admin import api_settings, setup_logger
from web_admin.restful_methods import RESTfulMethods
from authentications.utils import get_correlation_id_from_username
from web_admin.utils import calculate_page_range_from_page_info

logger = logging.getLogger(__name__)

IS_SUCCESS = {
    True: 'Success',
    False: 'Failed',
}


class SofFileList(TemplateView, RESTfulMethods):
    template_name = "reconcile/sof_file_list.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(SofFileList, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        currencies, success = self._get_currency_choices()
        default_end_date = datetime.today().strftime("%Y-%m-%d")
        default_start_date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        return render(request, self.template_name, {'currencies': currencies,
                                                    'start_date': default_start_date,
                                                    'end_date': default_end_date})

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start search sof file list ==========')

        opening_page_index = request.POST.get('current_page_index')
        is_on_us = int(request.POST.get('on_off_us_id'))
        source_of_fund = request.POST.get('source_of_fund_id')
        sof_partner_name = request.POST.get('sof_partner_name_id')
        currency = request.POST.get('currency_id')
        reconcile_status = int(request.POST.get('reconcile_status_id'))
        start_date = request.POST.get('from_created_timestamp')
        end_date = request.POST.get('to_created_timestamp')

        params = {}
        params['opening_page_index'] = opening_page_index

        if is_on_us >= 0:
            params['is_on_us'] = is_on_us
        if source_of_fund is not '' and source_of_fund is not None:
            params['source_of_fund'] = source_of_fund
        if sof_partner_name and not sof_partner_name.isspace():
            params['sof_code'] = sof_partner_name
        if currency and not currency.isspace():
            params['currency'] = currency
        if reconcile_status > 0:
            params['status_id'] = reconcile_status
        if start_date is not '':
            converted_start_date = datetime.strptime(start_date, "%Y-%m-%d")
            converted_start_date = converted_start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            params['from_last_updated_timestamp'] = converted_start_date
        if end_date is not '':
            converted_end_date = datetime.strptime(end_date, "%Y-%m-%d")
            converted_end_date = converted_end_date.replace(hour=23, minute=59, second=59)
            converted_end_date = converted_end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            params['to_last_updated_timestamp'] = converted_end_date

        context = {}
        try:
            data, page = self._search_file_list(params)
            context.update({'file_list': data, 'paginator': page,
                            'page_range': calculate_page_range_from_page_info(page)})
        except requests.Timeout:
            self.logger.error('========== Search SOF file list request timeout ==========')
            context.update(
                {'sof_file_list_time_out_msg': 'Search timeout, please try again or contact technical support'})

        currencies, success = self._get_currency_choices()
        context.update({'currencies': currencies,
                        'start_date': start_date,
                        'end_date': end_date})
        context.update(params)
        self.logger.info("========== Finish searching system user ==========")
        return render(request, self.template_name, context)

    def _search_file_list(self, params):
        self.logger.info('========== Start Searching SOF File List ==========')
        api_path = api_settings.SEARCH_RECONCILE_SOF_FILE_LIST

        response_json, success = self._post_method(
            api_path=api_path,
            func_description="Search sof File List",
            logger=logger,
            params=params,
            only_return_data=False
        )
        self.logger.info("data={}".format(response_json.get('data')))
        self.logger.info('========== Finish Searching SOF File List ==========')
        return response_json.get('data'), response_json.get('page')

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