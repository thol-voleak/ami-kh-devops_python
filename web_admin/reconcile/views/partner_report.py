import logging
from datetime import datetime, timedelta

import requests
from django.shortcuts import render
from django.views.generic.base import TemplateView
from web_admin import api_settings
from multiprocessing.pool import ThreadPool
from web_admin.restful_methods import RESTfulMethods
from web_admin.utils import setup_logger
from web_admin.utils import calculate_page_range_from_page_info

logger = logging.getLogger(__name__)

IS_SUCCESS = {
    True: 'Success',
    False: 'Failed',
}


class PartnerReport(TemplateView, RESTfulMethods):
    template_name = "reconcile/partner_report_result.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(PartnerReport, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Set first load default date
        default_end_date = datetime.today().strftime("%Y-%m-%d")
        default_start_date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

        data, success = self._get_service(-1)

        choices, success = self._get_service_group_and_currency_choices()
        context = {'from_created_timestamp': default_start_date,
                   'to_created_timestamp': default_end_date,
                   'service_get_url': api_settings.GET_SERVICE_BY_SERVICE_GROUP_URL,
                   'service_group_id': -1,
                   'choices': choices
                  }

        context['service_list'] = data
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start search partner report ==========')
        choices, success = self._get_service_group_and_currency_choices()

        context = super(PartnerReport, self).get_context_data(**kwargs)

        partner_file_id = context.get('partner_file_id')
        if partner_file_id is not None:
            partner_file_id = int(partner_file_id)

        opening_page_index = request.POST.get('current_page_index')
        on_off_us_id = int(request.POST.get('on_off_us_id'))
        service_group_id = request.POST.get('service_group_id')
        service_name = request.POST.get('service_id')
        agent_id = request.POST.get('partner_id')
        currency_id = request.POST.get('currency_id')
        reconcile_status_id = int(request.POST.get('reconcile_status_id'))
        reconcile_payment_type_id = request.POST.get('reconcile_payment_type_id')
        from_created_timestamp = request.POST.get('from_created_timestamp')
        to_created_timestamp = request.POST.get('to_created_timestamp')

        self.logger.info('On us/Off us: {}'.format(on_off_us_id))
        self.logger.info('Service group: {}'.format(service_group_id))
        self.logger.info('Service name: {}'.format(service_name))
        self.logger.info('Agent id: {}'.format(agent_id))
        self.logger.info('Currency: {}'.format(currency_id))
        self.logger.info('Reconcile status: {}'.format(reconcile_status_id))
        self.logger.info('Payment type: {}'.format(reconcile_payment_type_id))
        self.logger.info('Start date: {}'.format(from_created_timestamp))
        self.logger.info('End date: {}'.format(to_created_timestamp))

        service_group_id = int(service_group_id)

        params = {}
        params['opening_page_index'] = opening_page_index

        if partner_file_id is not None:
            params['partner_file_id'] = partner_file_id

        if on_off_us_id >= 0:
            params['is_on_us'] = (on_off_us_id == 1)

        if service_name is None:
            params['service_name'] = ''
        elif service_name != '':
            params['service_name'] = service_name

        if currency_id != '':
            params['currency'] = currency_id

        if agent_id is not None and agent_id != '':
            params['agent_id'] = int(agent_id)

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
            data, page, status_code = self._search_partner_report(params)
            if status_code == 500:
                self.logger.error('Search fail, please try again or contact technical support')
                request.session['partner_report_update_msg'] = 'Search fail, please try again or contact technical support'
            else:
                service_list, get_service_status = self._get_service(service_group_id)
                self.logger.info('Service group and currencies: {}'.format(choices))
                context.update(
                    {'paginator': page, 'page_range': calculate_page_range_from_page_info(page), 'service_list': service_list})

            context.update({'partner_report': data})

        except requests.Timeout as e:
            logger.error("Search Partner Report Timeout", e)
            request.session['partner_report_update_msg'] = 'Search timeout, please try again or contact technical support'

        context.update({'is_on_us': on_off_us_id,
                        'service_group_id': service_group_id,
                        'selected_service': service_name,
                        'agent_id': agent_id,
                        'currency_id': currency_id,
                        'choices': choices,
                        'reconcile_status_id': reconcile_status_id,
                        'reconcile_payment_type_id': reconcile_payment_type_id,
                        'from_created_timestamp': from_created_timestamp,
                        'to_created_timestamp': to_created_timestamp,
                        'partner_report_update_msg': self.request.session.pop('partner_report_update_msg', None)
                        })

        if partner_file_id is not None:
            context.update({'partner_file_id': partner_file_id})

        self.logger.info("========== Finish search partner report ==========")
        return render(request, self.template_name, context)

    def _search_partner_report(self, params):
        self.logger.info('========== Start Searching Partner Report ==========')
        api_path = api_settings.SEARCH_RECONCILE_PARTNER_REPORT

        response_json, success = self._post_method(
            api_path=api_path,
            func_description="Search partner Reconcile Report",
            logger=logger,
            params=params,
            only_return_data=False
        )
        self.logger.info("data={}".format(response_json.get('data')))
        self.logger.info('========== Finish Searching Partner Report ==========')
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
        self.logger.info('========== Start Getting Service Group ==========')
        url = api_settings.SERVICE_GROUP_LIST_URL

        self.logger.info('========== Finish Getting Service Group ==========')
        return self._get_method(url, "get services group list", logger, True)

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