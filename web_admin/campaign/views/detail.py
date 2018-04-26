from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from django.conf import settings
from django.shortcuts import render
import logging
from web_admin.api_logger import API_Logger
from braces.views import GroupRequiredMixin
from web_admin.api_settings import GET_RULE_AMOUNT_LIMIT, GET_CAMPAIGNS_DETAIL, GET_MECHANIC_LIST, GET_CONDITION_LIST, GET_COMPARISON_LIST, GET_CONDITION_DETAIL, GET_REWARD_LIST, GET_LIMITION_LIST, GET_CONDITION_FILTER

logger = logging.getLogger(__name__)


class CampaignDetail(GroupRequiredMixin, TemplateView, GetHeaderMixin):

    template_name = "campaign/detail.html"
    group_required = "CAN_VIEW_CAMPAIGN_DETAILS"
    login_url = 'web:permission_denied'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(CampaignDetail, self).dispatch(request, *args, **kwargs)

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def get(self, request, *args, **kwargs):
        context = super(CampaignDetail, self).get_context_data(**kwargs)
        self.logger.info('========== Start get campaign detail ==========')
        permissions = {'CAN_ADD_RULE_LIMIT': self.check_membership(["CAN_ADD_RULE_LIMIT"])}

        campaign_id = context['campaign_id']
        data = self.get_detail_campaign(campaign_id)
        amount_limit = self.get_campaign_amount_limit(campaign_id)
        mechanic_list = self.get_mechanic_list(campaign_id)
        mechanic_list = [x for x in mechanic_list if not x['is_deleted']]
        limit_values = []
        count_limit_values = 0;
        for i in amount_limit:
            if not i['is_deleted']:
                limit_values.append(i.get('limit_value'))
                count_limit_values += 1

        context.update({
            'data': data,
            'mechanic_list': mechanic_list,
            'limit_values': limit_values,
            'count_limit_values': count_limit_values,
            'permissions': permissions
        })

        self.logger.info('========== Finish get campaign detail ==========')
        return render(request, self.template_name, context)

    def get_mechanic_list(self, campaign_id):
        url = settings.DOMAIN_NAMES + GET_MECHANIC_LIST.format(bak_rule_id=campaign_id)
        self.logger.info('========== Start get mechanic list ==========')
        success, status_code, data  = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                               status_code=status_code)
        return data

    def get_detail_campaign(self, campaign_id):
        url = settings.DOMAIN_NAMES + GET_CAMPAIGNS_DETAIL.format(bak_rule_id=campaign_id)
        success, status_code, data  = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                               status_code=status_code)
        return data

    def get_campaign_amount_limit(self, campaign_id):
        url = settings.DOMAIN_NAMES + GET_RULE_AMOUNT_LIMIT.format(rule_id=campaign_id)
        self.logger.info('========== Start get campaign amount limit ==========')
        success, status_code, data = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                               status_code=status_code)
        self.logger.info('========== Finish get campaign amount limit ==========')
        return data

