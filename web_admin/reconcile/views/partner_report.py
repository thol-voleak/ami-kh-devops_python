import logging
from datetime import datetime, timedelta

import requests
from braces.views import GroupRequiredMixin
from django.shortcuts import render
from django.views.generic.base import TemplateView
from web_admin import api_settings, setup_logger
from multiprocessing.pool import ThreadPool
from web_admin.restful_methods_reconcile import RESTfulReconcileMethods
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.utils import calculate_page_range_from_page_info

logger = logging.getLogger(__name__)

IS_SUCCESS = {
    True: 'Success',
    False: 'Failed',
}


class PartnerReport(GroupRequiredMixin, TemplateView, RESTfulReconcileMethods):
    template_name = "reconcile/partner_report_result.html"
    logger = logger

    group_required = "CAN_GET_RECONCILE_REPORT_PARTNER_RECONCILE"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(PartnerReport, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Set first load default date
        default_end_date = datetime.today().strftime("%Y-%m-%d")
        default_start_date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

        context = {'from_created_timestamp': default_start_date,
                   'to_created_timestamp': default_end_date
                  }

        currencies, success = self._get_currency_choices()
        if success is True:
            context.update({'currencies':currencies})

        services_list, service_groups, service_group_id, success = self._get_service_group_and_services_list(-1)
        if success is True:
            context.update({'service_list': services_list, 'service_groups': service_groups, 'service_group_id': service_group_id})
        else:
            context.update({'partner_report_update_msg': 'Fail to get service group, please refresh the page or contact technical support'})

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start search partner report ==========')
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

        if reconcile_payment_type_id != '' and reconcile_payment_type_id != "-1":
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


        currencies, success = self._get_currency_choices()
        if success is True:
            context.update({'currencies': currencies})

        services_list, service_groups, service_group_id, success = self._get_service_group_and_services_list(service_group_id)
        if success is True:
            context.update({'service_list': services_list, 'service_groups': service_groups, 'service_group_id': service_group_id})
        else:
            context.update({'partner_report_update_msg': 'Fail to get service group, please refresh the page or contact technical support'})
            params['service_name'] = None
        try:
            data, page, status_code = self._search_partner_report(params)
            if status_code == 500:
                self.logger.error('Search fail, please try again or contact technical support')
                context.update(
                    {'partner_report_update_msg': 'Search fail, please try again or contact technical support'})
            else:
                context.update({'paginator': page, 'page_range': calculate_page_range_from_page_info(page),
                 'partner_report': data})

        except requests.Timeout as e:
            logger.error("Search Partner Report Timeout", e)
            context.update({'partner_report_update_msg': 'Search timeout, please try again or contact technical support'})

        context.update({'is_on_us': on_off_us_id,
                        'selected_service': service_name,
                        'agent_id': agent_id,
                        'currency_id': currency_id,
                        'reconcile_status_id': reconcile_status_id,
                        'reconcile_payment_type_id': reconcile_payment_type_id,
                        'from_created_timestamp': from_created_timestamp,
                        'to_created_timestamp': to_created_timestamp,
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
        service_groups = self._get_method(url, "get services group list", logger, True)
        return service_groups

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
            if success is True:
                service_group_id = int(service_group_id)
                services_list, success = self._get_service(service_group_id)
                if success is True:
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