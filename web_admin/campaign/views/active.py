from django.conf import settings
from web_admin import api_settings, setup_logger
from web_admin import ajax_functions
import logging
from braces.views import GroupRequiredMixin
from django.views.generic.base import TemplateView
from .detail import CampaignDetail
from web_admin.restful_client import RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.api_settings import UPDATE_CAMPAIGNS, GET_MECHANIC_LIST, GET_REWARD_LIST, GET_LIMITION_LIST
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from django.contrib import messages
from web_admin.api_logger import API_Logger
from django.http import JsonResponse
import json

logger = logging.getLogger(__name__)
logging.captureWarnings(True)

class ActiveCampaign(TemplateView, GetHeaderMixin):

    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ActiveCampaign, self).dispatch(request, *args, **kwargs)

    def post(self, request, campaign_id):
        self.logger.info('========== Start activate campaign ==========')
        url = settings.DOMAIN_NAMES + UPDATE_CAMPAIGNS.format(bak_rule_id=campaign_id)
        mechanic = self.get_mechanic_list(campaign_id)
        
        if mechanic == 'access_token_expired':
            return JsonResponse({"status": 1, "msg": ''})

        for i in mechanic:
            if i['is_deleted']:
                continue
            actions = self.get_rewards_list(campaign_id, i['id'])

            if actions == 'access_token_expired':
                return JsonResponse({"status": 1, "msg": ''})

            for action in actions:
                self.logger.info('========== Start get limittion list ==========')
                limition = self.get_limition_list(campaign_id, i['id'], action['id'])

                if limition == 'access_token_expired':
                    return JsonResponse({"status": 1, "msg": ''})

                self.logger.info('========== Finish get limittion list ==========')
                if len(limition) == 0:
                    self.logger.info('========== Finish get action list  ==========')
                    self.logger.info('========== Start get mechanic list ==========')
                    self.logger.info('========== Finish activate campaign ==========')
                    return JsonResponse({"status": 3, "msg": 'All campaign rewards needs a limitation before campaign can be activated'})
            self.logger.info('========== Finish get action list  ==========')
            self.logger.info('========== Start get mechanic list ==========')
        url = settings.DOMAIN_NAMES + UPDATE_CAMPAIGNS.format(bak_rule_id=campaign_id)
        params = {
            'is_active': True,
            'name': request.POST.get("campaign_name"),
            'description': request.POST.get("campaign_description")
        }
        result = ajax_functions._put_method(request, url, "", self.logger, params)
        self.logger.info('========== Finish activate campaign ==========')
        return result

    def get_mechanic_list(self, campaign_id):
        url = settings.DOMAIN_NAMES + GET_MECHANIC_LIST.format(bak_rule_id=campaign_id)
        self.logger.info('========== Start get mechanic list ==========')
        success, status_code, data  = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
            self.logger.info('========== Finish get mechanic list ==========')
            self.logger.info('========== Finish activate campaign ==========')
            return 'access_token_expired'
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                               status_code=status_code)
        return data

    def get_limition_list(self, campaign_id, mechanic_id, action_id):
        url = settings.DOMAIN_NAMES + GET_LIMITION_LIST.format(bak_rule_id=campaign_id, bak_mechanic_id=mechanic_id, bak_action_id=action_id)
        success, status_code, data  = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
            self.logger.info('========== Finish get limitation list ==========')
            self.logger.info('========== Finish get rewards list ==========')
            self.logger.info('========== Finish get mechanic list ==========')
            self.logger.info('========== Finish activate campaign ==========')
            return 'access_token_expired'
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                               status_code=status_code)
        return data

    def get_rewards_list(self, campaign_id, mechanic_id):
        url = settings.DOMAIN_NAMES + GET_REWARD_LIST.format(bak_rule_id=campaign_id, bak_mechanic_id=mechanic_id)
        self.logger.info('========== Start get action list ==========')
        success, status_code, data  = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
            self.logger.info('========== Finish get rewards list ==========')
            self.logger.info('========== Finish get mechanic list ==========')
            self.logger.info('========== Finish activate campaign ==========')
            return 'access_token_expired'
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                               status_code=status_code)
        return data