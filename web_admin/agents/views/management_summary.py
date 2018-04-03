from braces.views import GroupRequiredMixin
from web_admin import api_settings, setup_logger
from django.views.generic.base import TemplateView
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from django.shortcuts import redirect, render
from web_admin.restful_client import RestFulClient
from web_admin.api_logger import API_Logger
from web_admin.api_settings import SEARCH_RELATIONSHIP, RELATIONSHIP_TYPES_LIST
from web_admin.get_header_mixins import GetHeaderMixin
from agents.utils import _create_product_relation, check_permission_agent_management
from shop.utils import search_shop

import logging

logger = logging.getLogger(__name__)
logging.captureWarnings(True)


class AgentManagementSummary(GroupRequiredMixin, TemplateView, GetHeaderMixin):

    template_name = "agents/management_summary.html"
    group_required = "CAN_VIEW_PROFILE_MANAGEMENT"
    login_url = 'web:permission_denied'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AgentManagementSummary, self).dispatch(request, *args, **kwargs)

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def get(self, request, *args, **kwargs):
        context = super(AgentManagementSummary, self).get_context_data(**kwargs)
        body = {}
        body['user_id'] = int(context['agent_id'])

        permissions = check_permission_agent_management(self)
        if not permissions['CAN_ACCESS_SUMMARY_TAB']:
            if permissions['CAN_ACCESS_PRODUCT_CONFIGURATION_TAB']:
                return redirect('agents:agent_management_product',agent_id=int(context['agent_id']))
            elif permissions['CAN_ACCESS_SHOP_MANAGEMENT_TAB']:
                return redirect('agents:agent_management_shop', agent_id=int(context['agent_id']))
            elif permissions['CAN_ACCESS_RELATIONSHIP_TAB']:
                return redirect('agents:agent_management_relationship', agent_id=int(context['agent_id']))


        context.update(
            {'agent_id': int(context['agent_id']),
             'permissions': permissions
             })

        if permissions['CAN_ACCESS_RELATIONSHIP_TAB']:
            self.logger.info('========== Start getting Relationships list ==========')
            data, success, status_message = self._get_relationships(params=body)
            if success:
                relationships_list = data.get("relationships", [])
                summary_relationships = list(relationships_list)
                if len(relationships_list) > 10:
                    summary_relationships = relationships_list[:10]

                page = data.get("page", {})
                context.update(
                    {'search_count': page.get('total_elements', 0),
                     'summary_relationships': summary_relationships,
                     'relationship_list_length': len(relationships_list)
                     })

            self.logger.info('========== Finish getting Relationships list ==========')

        if permissions['CAN_ACCESS_PRODUCT_CONFIGURATION_TAB']:
            self.logger.info('========== Start getting product portfolio ==========')

            applicable_categories, applied_category = _create_product_relation(self, int(context['agent_id']))
            context.update({
                'applied_category': applied_category,
            })

            self.logger.info('========== Finish getting product portfolio ==========')

        if permissions['CAN_ACCESS_SHOP_MANAGEMENT_TAB']:
            self.logger.info('========== Start getting shop management ==========')
            shops = search_shop(self, {'agent_id': int(context['agent_id']), "paging": False})
            context.update({
                'shops': shops.get('shops', []),
            })
            self.logger.info('========== Finish getting shop management ==========')

        return render(request, self.template_name, context)

    def _get_relationships(self, params):

        api_path = SEARCH_RELATIONSHIP
        success, status_code, status_message, data = RestFulClient.post(
            url=api_path,
            headers=self._get_headers(),
            loggers=self.logger,
            params=params)

        data = data or {}
        API_Logger.post_logging(loggers=self.logger, params=params, response=data.get('relationships', []),
                                status_code=status_code, is_getting_list=True)

        return data, success, status_message
