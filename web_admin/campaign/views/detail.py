from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, api_settings
from web_admin.restful_client import RestFulClient
from django.views.generic.base import TemplateView
from web_admin.get_header_mixins import GetHeaderMixin
from django.conf import settings
from django.shortcuts import render
import logging
from braces.views import GroupRequiredMixin
from authentications.apps import InvalidAccessToken
from web_admin.api_settings import GET_CAMPAIGNS_DETAIL
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
        campaign_id = context['campaign_id']
        url = settings.DOMAIN_NAMES + GET_CAMPAIGNS_DETAIL.format(bak_rule_id=campaign_id)
        success, status_code, data  = RestFulClient.get(url=url, loggers=self.logger, headers=self._get_headers())
        if not success:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info("{}".format('access_token_expire'))
                raise InvalidAccessToken('access_token_expire')
        context.update({
            'data': data
        })
        return render(request, self.template_name, context)