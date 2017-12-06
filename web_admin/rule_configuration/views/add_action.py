from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.api_logger import API_Logger
from django.contrib import messages
from web_admin import api_settings, setup_logger, RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin
from braces.views import GroupRequiredMixin

from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)

class AddRuleAction(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    group_required = "CAN_CREATE_CAMPAIGN"
    login_url = 'web:permission_denied'
    raise_exception = False
    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = 'rule_configuration/add_action.html'
    logger = logger






