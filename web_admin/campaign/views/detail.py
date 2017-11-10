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
from authentications.apps import InvalidAccessToken
from web_admin.api_settings import GET_CAMPAIGNS_DETAIL, GET_MECHANIC_LIST, GET_CONDITION_DETAILS, GET_CONDITION_LIST
from django.contrib import messages


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
        campaign_id = context['campaign_id']
        data = self.get_detail_campaign(campaign_id)
        mechanic = self.get_mechanic_list(campaign_id)
        count = 0
        active_mechanic_count = 0
        for i in mechanic:
            if not i['is_deleted'] :
                active_mechanic_count += 1
            count += 1
            i['count'] = count
        context.update({
            'data': data,
            'active_mechanic_count': active_mechanic_count,
            'mechanic': mechanic,
            'len_mechanic': len(mechanic)
        })
        self.logger.info('========== Finish get mechanic list ==========')
        self.logger.info('========== Finish get campaign detail ==========')
        return render(request, self.template_name, context)

    def get_mechanic_list(self, campaign_id):
        url = settings.DOMAIN_NAMES + GET_MECHANIC_LIST.format(bak_rule_id=campaign_id)
        self.logger.info('========== Start get mechanic list ==========')
        success, status_code, data  = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                               status_code=status_code)
        if not success:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format('access_token_expire'))
                raise InvalidAccessToken('access_token_expire')
        return data

    def get_detail_campaign(self, campaign_id):
        url = settings.DOMAIN_NAMES + GET_CAMPAIGNS_DETAIL.format(bak_rule_id=campaign_id)
        success, status_code, data  = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                               status_code=status_code)
        if not success:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format('access_token_expire'))
                raise InvalidAccessToken('access_token_expire')
        return data


