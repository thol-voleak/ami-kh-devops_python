from braces.views import GroupRequiredMixin

from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger
from django.contrib import messages
from web_admin.api_settings import GET_AGENT_IDENTITY_URL
from web_admin.restful_methods import RESTfulMethods
from web_admin.restful_client import RestFulClient
from django.shortcuts import render
from django.views.generic.base import TemplateView
from web_admin.api_logger import API_Logger
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
logging.captureWarnings(True)


class AddAgentIdentities(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_ADD_AGENT_IDENTITIES"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = 'agents/add_agent_identities.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AddAgentIdentities, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== User go to Add Agent Identity page ==========')
        return render(request, self.template_name)