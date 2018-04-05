from braces.views import GroupRequiredMixin
from web_admin import api_settings, setup_logger
from django.views.generic.base import TemplateView
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from django.shortcuts import render, redirect
from web_admin.utils import calculate_page_range_from_page_info
from web_admin.get_header_mixins import GetHeaderMixin
from agents.utils import check_permission_agent_management
from shop.utils import search_shop
import logging

logger = logging.getLogger(__name__)


class AgentManagementShop(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    template_name = "agents/management_shop.html"
    group_required = "CAN_VIEW_PROFILE_MANAGEMENT"
    login_url = 'web:permission_denied'
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
        if not permissions['CAN_ACCESS_SHOP_MANAGEMENT_TAB']:
            return redirect('agents:agent_management_summary',
                            agent_id=int(agent_id))

        context = {"agent_id": agent_id, "permissions": permissions}
        opening_page_index = request.GET.get('current_page_index', 1)

        params = {
            "agent_id": agent_id,
            "paging": True,
            "page_index": int(opening_page_index)
        }

        shops = search_shop(self, params)
        page = shops.get('page', {})
        context.update({
            'shops': shops.get('shops', []),
            'paginator': page,
            'page_range': calculate_page_range_from_page_info(page),
            'total_result': page.get('total_elements', 0)
        })
        return render(request, self.template_name, context)

