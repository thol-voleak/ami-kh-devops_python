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
from web_admin.api_settings import GET_CAMPAIGNS_DETAIL, GET_MECHANIC_LIST, GET_CONDITION_LIST, GET_COMPARISON_LIST, GET_CONDITION_DETAIL, GET_REWARD_LIST, GET_LIMITION_LIST
from django.contrib import messages


logger = logging.getLogger(__name__)


class CampaignDetail(GroupRequiredMixin, TemplateView, GetHeaderMixin):

    template_name = "campaign/detail.html"
    group_required = "CAN_VIEW_CAMPAIGN_DETAILS"
    login_url = 'web:permission_denied'
    logger = logger
    person = {
        '@@user_id@@':'Actor who registered',
        '@@payer_user_id@@':'Actor that paid for the transaction',
        '@@payee_user_id@@':'Actor that received the transaction',
        '@@initiator_user_id@@':'Actor that created the transaction'
    }

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
            reward = {}
            if not i['is_deleted']:
                i['reward'] = None
                active_mechanic_count += 1
                i['count'] = active_mechanic_count
                i['condition_list'] = self.get_condition_list(campaign_id, i['id'])
                for condition in i['condition_list']:
                    condition['condition_detail'] = self.get_condition_detail(campaign_id, i['id'], condition['id'])
                    condition['comparison_list'] = self.get_comparison_list(campaign_id, i['id'], condition['id'])
                    self.logger.info('========== Finish get comparison list ==========')
                    self.logger.info('========== Finish get condition detail ==========')
                self.logger.info('========== Finish get condition list ==========')
                action = self.get_rewards_list(campaign_id, i['id'])
                action_id = None
                if len(action) > 0:
                    action = action[0]
                    action_id = action['id']
                    reward['reward_type'] = action['action_type']['name']
                    for j in action['action_data']:
                        if j['key_name'] == 'payee_user.user_id':
                            if j['key_value'] in self.person.keys():
                                reward['reward_to'] = self.person[j['key_value']]
                        if j['key_name'] == 'payee_user.user_type':
                            reward['recipient'] = j['key_value']
                        if j['key_name'] == 'amount':
                            reward['amount'] = j['key_value']
                if reward != {}:
                    i['reward'] = reward
                self.logger.info('========== Finish get action detail  ==========')
                if action_id:
                    limitation= self.get_limitation_list(campaign_id, i['id'], action_id)
                    self.logger.info('========== Finish get limitation list ==========')
                    i['limitation_list'] = []
                    for limitation in limitation:
                        if not limitation['is_deleted']:
                            for filter_limit in limitation['filters']:
                                if filter_limit['key_name'] == 'payee_user.user_id':
                                    if filter_limit['key_value'] in self.person.keys():
                                        limitation['reward_to'] = self.person[filter_limit['key_value']]
                                if filter_limit['key_name'] == 'payee_user.user_type':
                                    limitation['recipient'] = filter_limit['key_value']
                            i['limitation_list'].append(limitation)

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
        return data

    def get_detail_campaign(self, campaign_id):
        url = settings.DOMAIN_NAMES + GET_CAMPAIGNS_DETAIL.format(bak_rule_id=campaign_id)
        success, status_code, data  = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                               status_code=status_code)
        return data

    def get_condition_list(self, campaign_id, mechanic_id):
        url = settings.DOMAIN_NAMES + GET_CONDITION_LIST.format(bak_rule_id=campaign_id, bak_mechanic_id=mechanic_id)
        self.logger.info('========== Start get condition list ==========')
        success, status_code, data  = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                               status_code=status_code)
        return data

    def get_comparison_list(self, campaign_id, mechanic_id, condition_id):
        url = settings.DOMAIN_NAMES + GET_COMPARISON_LIST.format(bak_rule_id=campaign_id, bak_mechanic_id=mechanic_id, bak_condition_id=condition_id)
        self.logger.info('========== Start get comparison list ==========')
        success, status_code, data  = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                               status_code=status_code)
        return data

    def get_condition_detail(self, campaign_id, mechanic_id, condition_id):
        url = settings.DOMAIN_NAMES + GET_CONDITION_DETAIL.format(bak_rule_id=campaign_id, bak_mechanic_id=mechanic_id, bak_condition_id=condition_id)
        self.logger.info('========== Start get condition detail ==========')
        success, status_code, data  = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                               status_code=status_code)
        return data

    def get_rewards_list(self, campaign_id, mechanic_id):
        url = settings.DOMAIN_NAMES + GET_REWARD_LIST.format(bak_rule_id=campaign_id, bak_mechanic_id=mechanic_id)
        self.logger.info('========== Start get action list ==========')
        success, status_code, data  = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                               status_code=status_code)
        return data

    def get_limitation_list(self, campaign_id, mechanic_id, action_id):
        url = settings.DOMAIN_NAMES + GET_LIMITION_LIST.format(bak_rule_id=campaign_id, bak_mechanic_id=mechanic_id, bak_action_id=action_id)
        self.logger.info('========== Start get limitation list ==========')
        success, status_code, data  = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                               status_code=status_code)
        return data


