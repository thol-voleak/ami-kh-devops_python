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


class SofReport(TemplateView, RESTfulMethods):
    template_name = "reconcile/sof_report_result.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(SofReport, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        currencies, success = self._get_currency_choices()

        # Set first load default date
        default_end_date = datetime.today().strftime("%Y-%m-%d")
        default_start_date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

        context = {'from_created_timestamp': default_start_date,
                   'to_created_timestamp': default_end_date,
                   'currencies': currencies}

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start search sof report ==========')
        context = super(SofReport, self).get_context_data(**kwargs)

        sof_file_id = context.get('sofFileId')
        if sof_file_id is not None:
            sof_file_id = int(sof_file_id)
        opening_page_index = request.POST.get('current_page_index')
        on_off_us_id = int(request.POST.get('on_off_us_id'))
        source_of_fund_id = request.POST.get('source_of_fund_id')
        sof_code = request.POST.get('sof_partner_name_id')
        currency_id = request.POST.get('currency_id')
        reconcile_status_id = int(request.POST.get('reconcile_status_id'))
        reconcile_payment_type_id = request.POST.get('reconcile_payment_type_id')
        from_created_timestamp = request.POST.get('from_created_timestamp')
        to_created_timestamp = request.POST.get('to_created_timestamp')

        self.logger.info('On us/Off us: {}'.format(on_off_us_id))
        self.logger.info('Source of fund: {}'.format(source_of_fund_id))
        self.logger.info('Source of fund partner name: {}'.format(sof_code))
        self.logger.info('Currency: {}'.format(currency_id))
        self.logger.info('Reconcile status: {}'.format(reconcile_status_id))
        self.logger.info('Payment type: {}'.format(reconcile_payment_type_id))
        self.logger.info('Start date: {}'.format(from_created_timestamp))
        self.logger.info('End date: {}'.format(to_created_timestamp))

        params = {}
        params['opening_page_index'] = opening_page_index

        if sof_file_id is not None:
            params['sof_file_id'] = sof_file_id

        if on_off_us_id >= 0:
            params['is_on_us'] = (on_off_us_id == 1)
        if source_of_fund_id:
            params['source_of_fund'] = source_of_fund_id
        if sof_code:
            params['sof_code'] = sof_code
        if currency_id:
            params['currency'] = currency_id
        if reconcile_status_id >=0:
            params['status_id'] = reconcile_status_id
        if reconcile_payment_type_id != '' and int(reconcile_payment_type_id) >= 0:
            params['payment_type'] = reconcile_payment_type_id

        if from_created_timestamp is not '':
            new_from_created_timestamp = datetime.strptime(from_created_timestamp, "%Y-%m-%d")
            new_from_created_timestamp = new_from_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            params['from_last_updated_timestamp'] = new_from_created_timestamp

        if to_created_timestamp is not '':
            new_to_created_timestamp = datetime.strptime(to_created_timestamp, "%Y-%m-%d")
            new_to_created_timestamp = new_to_created_timestamp.replace(hour=23, minute=59, second=59)
            new_to_created_timestamp = new_to_created_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            params['to_last_updated_timestamp'] = new_to_created_timestamp
        try:
            data, page, status_code = self._search_sof_report(params)
            if status_code == 500:
                self.logger.error('Search fail, please try again or contact technical support')
                request.session['sof_report_update_msg'] = 'Search fail, please try again or contact technical support'
            else:
                context.update({'paginator': page, 'page_range': calculate_page_range_from_page_info(page)})
            context.update({'sof_report': data})

        except requests.Timeout as e:
            logger.error("Search Sof Report Timeout", e)
            request.session['sof_report_update_msg'] = 'Search timeout, please try again or contact technical support'

        currencies, success = self._get_currency_choices()
        self.logger.info('currencies: {}'.format(currencies))
        context.update({'is_on_us': on_off_us_id,
                        'source_of_fund': source_of_fund_id,
                        'sof_code': sof_code,
                        'currency_id': currency_id,
                        'currencies': currencies,
                        'reconcile_status_id': reconcile_status_id,
                        'reconcile_payment_type_id': reconcile_payment_type_id,
                        'from_created_timestamp': from_created_timestamp,
                        'to_created_timestamp': to_created_timestamp
                        })
        context.update({'sof_report_update_msg': self.request.session.pop('sof_report_update_msg', None)})
        if sof_file_id is not None:
            context.update({'sof_file_id': sof_file_id})

        self.logger.info("========== Finish search sof report ==========")
        return render(request, self.template_name, context)

    def _search_sof_report(self, params):
        self.logger.info('========== Start Searching Sof Report ==========')
        api_path = api_settings.SEARCH_RECONCILE_SOF_REPORT

        response_json, success = self._post_method(
            api_path=api_path,
            func_description="Search sof Reconcile Report",
            logger=logger,
            params=params,
            only_return_data=False
        )
        self.logger.info("data={}".format(response_json.get('data')))
        self.logger.info('========== Finish Searching Sof Report ==========')
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