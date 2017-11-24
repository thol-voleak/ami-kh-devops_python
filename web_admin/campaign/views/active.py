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

class ActiveCampaign(CampaignDetail):

    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ActiveCampaign, self).dispatch(request, *args, **kwargs)

    def post(self, request, campaign_id):
        self.logger.info('========== Start active campaign ==========')
        url = settings.DOMAIN_NAMES + UPDATE_CAMPAIGNS.format(bak_rule_id=campaign_id)
        mechanic = self.get_mechanic_list(campaign_id)
        count_mechanic = 0
        for i in mechanic:
            actions = self.get_rewards_list(campaign_id, i['id'])
            count_action = 0;
            for action in actions:
                limition = self.get_limition_list(campaign_id, i['id'], action['id'])
                if len(limition) == 0:
                    return JsonResponse({"status": 3, "msg": 'All campaign rewards needs a limitation before campaign can be activated'})
                else:
                    count_action += 1
            if count_action == len(actions):
                count_mechanic += 1

        if count_mechanic == len(mechanic):
                url = settings.DOMAIN_NAMES + UPDATE_CAMPAIGNS.format(bak_rule_id=campaign_id)
                params = {
                    'is_active': True,
                    'name': request.POST.get("campaign_name"),
                    'description': request.POST.get("campaign_description")
                }
                result = ajax_functions._put_method(request, url, "", self.logger, params)
                self.logger.info('========== Finish active campaign ==========')
                return result

    def get_limition_list(self, campaign_id, mechanic_id, action_id):
        url = settings.DOMAIN_NAMES + GET_LIMITION_LIST.format(bak_rule_id=campaign_id, bak_mechanic_id=mechanic_id, bak_action_id=action_id)
        self.logger.info('========== Start get limittion list ==========')
        success, status_code, data  = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                               status_code=status_code)
        return data

