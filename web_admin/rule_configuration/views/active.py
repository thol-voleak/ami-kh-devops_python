from django.conf import settings
from web_admin import api_settings, setup_logger
from web_admin import ajax_functions
import logging
from braces.views import GroupRequiredMixin
from django.views.generic.base import TemplateView
from .detail import RuleDetail
from web_admin.restful_client import RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.api_settings import UPDATE_CAMPAIGNS, GET_RULE_MECHANIC_LIST, GET_RULE_REWARD_LIST, GET_RULE_CONDITION_LIST
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from django.contrib import messages
from web_admin.api_logger import API_Logger
from django.http import JsonResponse
import json

logger = logging.getLogger(__name__)
logging.captureWarnings(True)

class ActiveRule(TemplateView, GetHeaderMixin):
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ActiveRule, self).dispatch(request, *args, **kwargs)

    def post(self, request, rule_id):
        self.logger.info('========== Start activate rule ==========')
        url = settings.DOMAIN_NAMES + UPDATE_CAMPAIGNS.format(bak_rule_id=rule_id)
        is_able_to_activate = False
        mechanic = self.get_mechanic_list(rule_id)
        if mechanic == 'access_token_expired':
            return JsonResponse({"status": 1, "msg": ''})
        if not len(mechanic):
            return JsonResponse({"status": 3, "msg": 'Rule ID {} cannot be activated because this rule ID has to include at least 1 mechanic, 1 condition and 1 action'.format(rule_id)})
        else:
            mechanic = [i for i in mechanic if not i.get('is_deleted')]
            for i in mechanic:
                condition_list = self.get_condition_list(rule_id, i['id'])
                if condition_list == 'access_token_expired':
                    return JsonResponse({"status": 1, "msg": ''})
                self.logger.info('========== Finish get condition list ==========')
                condition_list = [i for i in condition_list if not i.get('is_deleted')]
                if len(condition_list) == 0:
                    continue
                action = self.get_rewards_list(rule_id, i['id'])
                if action == 'access_token_expired':
                    return JsonResponse({"status": 1, "msg": ''})
                self.logger.info('========== Finish get action list ==========')
                action = [i for i in action if not i.get('is_deleted')]
                if len(action) == 0:
                    continue
                if len(condition_list) > 0 and len(action) > 0:
                    is_able_to_activate = True
                    break
            if is_able_to_activate:
                params = {
                        'is_active': True,
                        'name': request.POST.get("rule_name"),
                        'description': request.POST.get("rule_description")
                }
                result = ajax_functions._put_method(request, url, "", self.logger, params)
                self.logger.info('========== Finish activate rule ==========')
                return result
            self.logger.info('========== Finish activate rule ==========')
            return JsonResponse({"status": 3, "msg": 'Rule ID {} cannot be activated because this rule ID has to include at least 1 mechanic, 1 condition and 1 action'.format(rule_id)})

    def get_rewards_list(self, rule_id, mechanic_id):
        url = settings.DOMAIN_NAMES + GET_RULE_REWARD_LIST.format(rule_id=rule_id, mechanic_id=mechanic_id)
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

    def get_condition_list(self, rule_id, mechanic_id):
        url = settings.DOMAIN_NAMES + GET_RULE_CONDITION_LIST.format(rule_id=rule_id, mechanic_id=mechanic_id)
        self.logger.info('========== Start get condition list ==========')
        success, status_code, data  = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
            self.logger.info('========== Finish get condition list ==========')
            self.logger.info('========== Finish get mechanic list ==========')
            self.logger.info('========== Finish activate campaign ==========')
            return 'access_token_expired'
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                               status_code=status_code)
        return data

    def get_mechanic_list(self, rule_id):
        url = settings.DOMAIN_NAMES + GET_RULE_MECHANIC_LIST.format(rule_id=rule_id)
        self.logger.info('========== Start get mechanic list ==========')
        success, status_code, data  = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
            self.logger.info('========== Finish get mechanic list ==========')
            self.logger.info('========== Finish activate campaign ==========')
            return 'access_token_expired'
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                               status_code=status_code)
        return data

