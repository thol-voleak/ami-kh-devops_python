from django.conf import settings
from web_admin import api_settings, setup_logger
from web_admin import ajax_functions
import logging
from braces.views import GroupRequiredMixin
from django.views.generic.base import TemplateView
from .detail import RuleDetail
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

class InactiveRule(TemplateView, GetHeaderMixin):
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(InactiveRule, self).dispatch(request, *args, **kwargs)

    def post(self, request, rule_id):
        self.logger.info('========== Start inactivate rule ==========')
        url = settings.DOMAIN_NAMES + UPDATE_CAMPAIGNS.format(bak_rule_id=rule_id)
        params = {
            'is_active': False,
            'name': request.POST.get("rule_name"),
            'description': request.POST.get("rule_description")
        }
        result = ajax_functions._put_method(request, url, "", self.logger, params)
        self.logger.info('========== Finish inactivate rule ==========')
        return result