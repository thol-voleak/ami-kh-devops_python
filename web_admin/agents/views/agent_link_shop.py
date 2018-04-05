from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from shop.utils import get_all_shop_type, get_all_shop_category
from web_admin import api_settings, setup_logger

from django.views.generic.base import TemplateView
from django.conf import settings
from django.shortcuts import render
from datetime import datetime , timedelta
from braces.views import GroupRequiredMixin
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin.restful_client import RestFulClient
from web_admin.api_logger import API_Logger
from shop.utils import search_shop


import logging

logger = logging.getLogger(__name__)


class AgentLinkShop(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    template_name = 'agents/agent_link_shop.html'
    group_required = 'CAN_LINK_SHOP'
    login_url = 'web:permission_denied'
    raise_exception = False
    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AgentLinkShop, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        permissions = {}
        permissions['CAN_ADD_SHOP'] = self.check_membership(["CAN_ADD_SHOP"])
        agent_id = kwargs["agent_id"]
        form = {}
        context = {"form": form, "agent_id": agent_id, 'permissions':permissions}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        permissions = {}
        permissions['CAN_ADD_SHOP'] = self.check_membership(["CAN_ADD_SHOP"])
        agent_id = kwargs["agent_id"]
        form = request.POST
        context = {'form': form, "agent_id": agent_id, 'permissions':permissions}

        params = {
            "paging": False,
            "is_deleted": False
        }

        if form['shop_id']:
            params['id'] = form['shop_id']

        if form['shop_name']:
            params['name'] = form['shop_name']

        shops = search_shop(self, params)
        context['shop_list'] = shops['shops']
        return render(request, self.template_name, context)