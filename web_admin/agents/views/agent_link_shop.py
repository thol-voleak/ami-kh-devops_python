from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from shop.utils import get_all_shop_type, get_all_shop_category
from web_admin import api_settings, setup_logger

from django.views.generic.base import TemplateView
from django.conf import settings
from django.shortcuts import render
from datetime import datetime , timedelta
from braces.views import GroupRequiredMixin
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.utils import calculate_page_range_from_page_info
from web_admin.restful_client import RestFulClient
from authentications.apps import InvalidAccessToken
from web_admin.api_logger import API_Logger


import logging

logger = logging.getLogger(__name__)


class AgentLinkShop(TemplateView, GetHeaderMixin):
    template_name = 'agents/agent_link_shop.html'
    raise_exception = False
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AgentLinkShop, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        agent_id = kwargs["agent_id"]
        form = {}
        context = {"form": form, "agent_id": agent_id}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        agent_id = kwargs["agent_id"]
        form = request.POST
        context = {'form': form, "agent_id": agent_id}

        return render(request, self.template_name, context)