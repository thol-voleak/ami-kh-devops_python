from django.conf import settings
from web_admin import api_settings, setup_logger
from web_admin import ajax_functions
import logging
from braces.views import GroupRequiredMixin
from django.views.generic.base import TemplateView
from .detail import CampaignDetail
from web_admin.restful_client import RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.api_settings import UPDATE_CAMPAIGNS, GET_MECHANIC_LIST, GET_REWARD_LIST
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from django.contrib import messages
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
        params = {
            'is_active': True,
            'name': request.POST.get("campaign_name"),
            'description': request.POST.get("campaign_description")
        }
        result = ajax_functions._put_method(request, url, "", self.logger, params)
        self.logger.info('========== Finish active campaign ==========')
        return result

