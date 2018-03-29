from braces.views import GroupRequiredMixin
from web_admin import api_settings, setup_logger
from django.views.generic.base import TemplateView
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from django.shortcuts import redirect, render
from web_admin.restful_client import RestFulClient
from web_admin.api_logger import API_Logger
from web_admin.get_header_mixins import GetHeaderMixin
from django.contrib import messages
from agents.utils import check_permission_agent_management
import logging

logger = logging.getLogger(__name__)


class AgentManagementShop(TemplateView, GetHeaderMixin):
    template_name = "agents/management_shop.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AgentManagementShop, self).dispatch(request, *args, **kwargs)

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def get(self, request, *args, **kwargs):
        agent_id = kwargs['agent_id']
        permissions = check_permission_agent_management(self)
        context = {"agent_id": agent_id, "permissions": permissions}
        return render(request, self.template_name, context)