from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
import logging
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.api_logger import API_Logger
from braces.views import GroupRequiredMixin
from django.contrib import messages


logger = logging.getLogger(__name__)
from django.shortcuts import render, redirect
import logging

logger = logging.getLogger(__name__)


class BalanceSummary(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    template_name = "balance_summary.html"
    group_required = "CAN_VIEW_BALANCE_SUMMARY"
    login_url = 'web:permission_denied'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(BalanceSummary, self).dispatch(request, *args, **kwargs)

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def get(self, request, *args, **kwargs):
        if not check_permissions_by_user(self.request.user, "CAN_VIEW_BALANCE_SUMMARY"):
            return redirect('web:permission_denied')

        self.logger.info('========== Start render Balance Summary page ==========')

        self.logger.info('========== Start getting customer summary ==========')
        customer_summary, is_get_customer_summary_success = self._get_customer_summary()
        self.logger.info('========== Finish getting customer summary ==========')

        if is_get_customer_summary_success:
            cus_total_sofs = 0
            for item in customer_summary['sofs']:
                cus_total_sofs += item.get('total_sof', 0)
            customer_summary['total_sof_card'] = cus_total_sofs

        self.logger.info('========== Start getting agent summary ==========')
        agent_summary, is_get_agent_summary_success = self._get_agent_summary()
        self.logger.info('========== Finish getting agent summary ==========')

        # get agent total soft card and currency balance list
        if is_get_agent_summary_success:
            sofs = agent_summary['agent_types'][0]['sofs']
            agent_summary['sofs'] = []

            for sof in sofs:
                currency = {'currency': sof['currency'], 'total_balance': 0}
                agent_summary['sofs'].append(currency)

            agent_total_sofs = 0
            for item in agent_summary['agent_types']:
                for sof in item['sofs']:
                    agent_total_sofs += sof.get('total_sof', 0)
                    for currency in agent_summary['sofs']:
                        if currency['currency'] == sof['currency']:
                            currency['total_balance'] += sof['total_balance']

            agent_summary['agent_total_sofs'] = agent_total_sofs

            # get agent profile number
            agent_total_profile = 0
            for item in agent_summary['agent_types']:
                agent_total_profile += item.get('total_profile', 0)

            agent_summary['agent_total_profile'] = agent_total_profile

        if is_get_agent_summary_success and is_get_customer_summary_success:
            context ={
                'customer_summary': customer_summary,
                'agent_summary': agent_summary,
                'is_get_agent_summary_success': 1,
                'is_get_customer_summary_success': 1
            }
        elif is_get_agent_summary_success and not is_get_customer_summary_success:
            context = {
                'agent_summary': agent_summary,
                'is_get_agent_summary_success': 1,
                'is_get_customer_summary_success': 0
            }
        elif not is_get_agent_summary_success and is_get_customer_summary_success:
            context = {
                'customer_summary': customer_summary,
                'is_get_agent_summary_success': 0,
                'is_get_customer_summary_success': 1
            }
        else:
            context = {
                'is_get_agent_summary_success': 0,
                'is_get_customer_summary_success': 0
            }

        self.logger.info('========== Finish render Balance Summary page ==========')

        return render(request, self.template_name, context)

    def _get_customer_summary(self):
        url = api_settings.GET_CUSTOMER_BALANCE
        url = 'http://localhost:7357/get_agent_summary'
        is_success, status_code, status_message, data = RestFulClient.post(url=url,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params={})

        API_Logger.post_logging(loggers=self.logger, params={}, response=data,
                                status_code=status_code, is_getting_list=False)

        if not is_success:
            data = {}
        return data, is_success

    def _get_agent_summary(self):
        url = api_settings.GET_AGENT_SUMMARY
        url = 'http://localhost:7357/get_agent_summary'
        is_success, status_code, status_message, data = RestFulClient.post(url=url,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params={})
        API_Logger.post_logging(loggers=self.logger, params={}, response=data,
                                status_code=status_code, is_getting_list=False)
        if not is_success:
            data = {}
        return data, is_success
