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
        customer_summary = self._get_customer_summary()
        self.logger.info('========== Finish getting customer summary ==========')
        data = [
            {'agent_type':'company',
            'profile':'human',
            'amount':'1000',
            'fee':'50',
            'currency':'vnd'}
        ]

        cus_total_sofs = 0
        for item in customer_summary['sofs']:
            cus_total_sofs += item.get('total_sof', 0)

        context ={
            'data': data,
            'customer_summary': customer_summary,
            'cus_total_sofs': cus_total_sofs,
            'cus_sofs': customer_summary['sofs']
        }

        self.logger.info('========== Finish render Balance Summary page ==========')

        return render(request, self.template_name, context)

    def _get_customer_summary(self):
        is_success, status_code, status_message, data = RestFulClient.post(url=api_settings.GET_CUSTOMER_BALANCE,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params={})

        API_Logger.post_logging(loggers=self.logger, params={}, response=data,
                                status_code=status_code, is_getting_list=False)

        if not is_success:
            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )
            data = {}
        return data
