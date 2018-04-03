import logging

from braces.views import GroupRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from authentications.utils import get_correlation_id_from_username
from web_admin import RestFulClient
from web_admin import setup_logger
from web_admin.api_logger import API_Logger
from web_admin.api_settings import GET_CAMPAIGNS_DETAIL, GET_RULE_AMOUNT_LIMIT, CREATE_RULE_AMOUNT_LIMIT
from web_admin.get_header_mixins import GetHeaderMixin

logger = logging.getLogger(__name__)

class AmountLimit(TemplateView, GetHeaderMixin):
    # group_required = "CAN_ADD_RULE_LIMIT"
    # login_url = 'web:permission_denied'

    template_name = "campaign/amount_limit.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AmountLimit, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start showing Add rule limit page page ==========')
        context = super(AmountLimit, self).get_context_data(**kwargs)
        campaign_id = context['campaign_id']
        campaign = self.get_campaign_detail(campaign_id)
        amount_limit = self.get_campaign_amount_limit(campaign_id)
        context.update({
            'campaign': campaign,
            'current_amount_limit': amount_limit
        })

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start adding rule limit ==========')
        params = {
            "limit_type": 'amount-per-user',
            "limit_value": float(request.POST.get('limit_to_value')),
            "filters": []
        }

        context = super(AmountLimit, self).get_context_data(**kwargs)
        campaign_id = context['campaign_id']
        url = CREATE_RULE_AMOUNT_LIMIT.format(rule_id=campaign_id)
        success, status_code, status_message, data = RestFulClient.post(url=url,
                                          headers=self._get_headers(), loggers=self.logger, params=params)
        API_Logger.get_logging(loggers=self.logger, params=params, response=data,
                               status_code=status_code)
        if success:
            request.session['rule_amount_limit_create_msg'] = 'Added data successfully'
            self.logger.info('========== Finished adding rule limit ==========')
            messages.add_message(
                request,
                messages.SUCCESS,
                'Amount Limit Added'
            )
            return redirect('campaign:amount_limit', campaign_id=campaign_id)
        elif status_message == 'timeout':
            messages.add_message(
                request,
                messages.ERROR,
                'Sorry, Request timeout. Please try again'
            )
        else:
            context = {
                'rule_amount_limit_info': params,
                'error_msg': ''
            }
        self.logger.info('========== Finished adding rule limit ==========')
        return render(request, 'campaign/amount_limit.html', context)

    def get_campaign_detail(self, campaign_id):
        url = GET_CAMPAIGNS_DETAIL.format(bak_rule_id=campaign_id)
        success, status_code, data = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                               status_code=status_code)
        return data

    def get_campaign_amount_limit(self, campaign_id):
        url = GET_RULE_AMOUNT_LIMIT.format(rule_id=campaign_id)
        success, status_code, data = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                               status_code=status_code)
        return data
