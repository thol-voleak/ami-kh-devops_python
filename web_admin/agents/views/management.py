from braces.views import GroupRequiredMixin
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin import api_settings, setup_logger
from django.views.generic.base import TemplateView
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from django.shortcuts import redirect, render
from web_admin.restful_client import RestFulClient
from web_admin.utils import calculate_page_range_from_page_info
from web_admin.api_logger import API_Logger
from web_admin.api_settings import SEARCH_RELATIONSHIP

import logging

logger = logging.getLogger(__name__)
logging.captureWarnings(True)


class AgentManagement(GroupRequiredMixin, TemplateView, GetHeaderMixin):

    template_name = "agents/management.html"
    group_required = "CAN_VIEW_PROFILE_MANAGEMENT"
    login_url = 'web:permission_denied'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AgentManagement, self).dispatch(request, *args, **kwargs)

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AgentManagement, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(AgentManagement, self).get_context_data(**kwargs)
        body = {}
        body['user_id'] = int(context['agent_id'])

        permissions = {}
        permissions['CAN_ACCESS_RELATIONSHIP_TAB'] = self.check_membership(['CAN_ACCESS_RELATIONSHIP_TAB'])
        permissions['CAN_ACCESS_SUMMARY_TAB'] = self.check_membership(['CAN_ACCESS_SUMMARY_TAB'])
        permissions['CAN_SEARCH_RELATIONSHIP'] = self.check_membership(['CAN_SEARCH_RELATIONSHIP'])
        default_tab = 0
        if not permissions['CAN_ACCESS_SUMMARY_TAB']:
            default_tab = 1
        context.update(
            {'agent_id': int(context['agent_id']),
             'permissions': permissions,
             'default_tab': default_tab
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
                     'relationships': relationships_list,
                     'summary_relationships': summary_relationships,
                     })

            self.logger.info('========== Finish getting Relationships list ==========')

        return render(request, self.template_name, context)

    def _get_relationships(self, params):
        self.logger.info('========== Start searching agent ==========')

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