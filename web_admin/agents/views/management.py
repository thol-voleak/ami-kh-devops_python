from braces.views import GroupRequiredMixin
from web_admin.get_header_mixins import GetHeaderMixin
from web_admin import api_settings, setup_logger
from django.views.generic.base import TemplateView
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from django.shortcuts import redirect, render
from web_admin.restful_client import RestFulClient
from web_admin.utils import calculate_page_range_from_page_info
from web_admin.api_logger import API_Logger
from web_admin.api_settings import SEARCH_RELATIONSHIP, RELATIONSHIP_TYPES_LIST
from web_admin.get_header_mixins import GetHeaderMixin
from authentications.apps import InvalidAccessToken

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
        relationship_type_id = []
        context.update(
            {'agent_id': int(context['agent_id']),
             'permissions': permissions,
             'relationship_types': self._get_relationship_types(),
             'relationship_type_id':relationship_type_id,
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
    def _get_relationship_types(self):
        is_success, status_code, data = RestFulClient.get(
            url=RELATIONSHIP_TYPES_LIST,
            headers=self._get_headers(),
            loggers=self.logger)
        if is_success:
            for i in data:
                if i['name'] == 'FL-Agent':
                    i['name'] = 'Frontline-Agent'
            return data
        elif status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
            self.logger.info("{}".format(data))
            raise InvalidAccessToken(data)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start searching relationship ==========')
        params = {}
        permissions = {}
        permissions['CAN_ACCESS_RELATIONSHIP_TAB'] = self.check_membership(['CAN_ACCESS_RELATIONSHIP_TAB'])
        permissions['CAN_ACCESS_SUMMARY_TAB'] = self.check_membership(['CAN_ACCESS_SUMMARY_TAB'])
        permissions['CAN_SEARCH_RELATIONSHIP'] = self.check_membership(['CAN_SEARCH_RELATIONSHIP'])
        agent_id = int(kwargs.get('agent_id'))
        list_relationship_type = request.POST.getlist('list_relationship_type')
        partner_role = request.POST.get('partner_role')
        relationship_partner_id = request.POST.get('relationship_partner_id')
        # params['paging'] = False
        # params['page_index'] = 0
        if list_relationship_type:
            list_relationship_type = [int(i) for i in list_relationship_type]
            params['relationship_type_ids'] = list_relationship_type
        if relationship_partner_id:
            if partner_role == 0:
                params['user_id'] = relationship_partner_id
            elif partner_role == 1:
                params['main_user_id'] = relationship_partner_id
            elif partner_role == 2:
                params['sub_user_id'] = relationship_partner_id
        else:
            params['user_id'] = agent_id

        data, success, status_message = self._get_relationships(params=params)
        if success:
            relationships_list = data.get("relationships", [])
            summary_relationships = list(relationships_list)
            if len(relationships_list) > 10:
                summary_relationships = relationships_list[:10]

            page = data.get("page", {})
 
            context = {
                    'agent_id':agent_id,
                    'permissions': permissions,
                    'search_count': page.get('total_elements', 0),
                    'relationships': relationships_list,
                    'summary_relationships': summary_relationships,
                    'relationship_type_id':list_relationship_type,
                    'relationship_types': self._get_relationship_types(),
                    'default_tab': 1
                }
        self.logger.info('========== finish search relationship ==========')
        
        return render(request, self.template_name, context)



        
