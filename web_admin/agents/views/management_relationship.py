from braces.views import GroupRequiredMixin
from web_admin import api_settings, setup_logger
from django.views.generic.base import TemplateView
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from django.shortcuts import redirect, render
from web_admin.restful_client import RestFulClient
from web_admin.api_logger import API_Logger
from web_admin.api_settings import SEARCH_RELATIONSHIP, RELATIONSHIP_TYPES_LIST
from web_admin.get_header_mixins import GetHeaderMixin
from authentications.apps import InvalidAccessToken
from agents.utils import check_permission_agent_management

import logging

logger = logging.getLogger(__name__)
logging.captureWarnings(True)


class AgentManagementRelationship(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    template_name = "agents/management_relationship.html"
    group_required = "CAN_VIEW_PROFILE_MANAGEMENT"
    login_url = 'web:permission_denied'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AgentManagementRelationship, self).dispatch(request, *args, **kwargs)

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def get(self, request, *args, **kwargs):
        context = super(AgentManagementRelationship, self).get_context_data(**kwargs)
        body = {}
        body['user_id'] = int(context['agent_id'])

        permissions = check_permission_agent_management(self)
        if not permissions['CAN_ACCESS_RELATIONSHIP_TAB']:
            return redirect('agents:agent_management_summary', agent_id=int(context['agent_id']))
        permissions['CAN_SEARCH_RELATIONSHIP'] = self.check_membership(['CAN_SEARCH_RELATIONSHIP'])
        permissions['CAN_DELETE_AGENT_RELATIONSHIP'] = self.check_membership(['CAN_DELETE_AGENT_RELATIONSHIP'])
        permissions['CAN_SHARE_AGENT_BENEFIT'] = self.check_membership(['CAN_SHARE_AGENT_BENEFIT'])
        permissions['CAN_ADD_AGENT_RELATIONSHIP'] = self.check_membership(['CAN_ADD_AGENT_RELATIONSHIP'])
        relationship_type_id = []
        context.update(
            {'agent_id': int(context['agent_id']),
             'permissions': permissions,
             'relationship_types': self._get_relationship_types(),
             'relationship_type_id': relationship_type_id
             })

        self.logger.info('========== Start getting Relationships list ==========')
        data, success, status_message = self._get_relationships(params=body)
        if success:
            relationships_list = data.get("relationships", [])
            relationships_list = [relationship for relationship in relationships_list if not relationship['is_deleted']]
            summary_relationships = list(relationships_list)
            if len(relationships_list) > 10:
                summary_relationships = relationships_list[:10]

            page = data.get("page", {})
            context.update(
                {'search_count': len(relationships_list),
                 'relationships': relationships_list,
                 'summary_relationships': summary_relationships,
                 'relationship_list_length': len(relationships_list)
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
        self.logger.info('========== Start getting relationship types ==========')
        is_success, status_code, data = RestFulClient.get(
            url=RELATIONSHIP_TYPES_LIST,
            headers=self._get_headers(),
            loggers=self.logger)
        if is_success:
            self.logger.info('Response_content: {}'.format(data))
            self.logger.info('========== finish get relationship types ==========')
            for i in data:
                if i['name'] == 'FL-Agent':
                    i['name'] = 'Frontline-Agent'
            return data
        elif status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
            self.logger.info("{}".format(data))
            raise InvalidAccessToken(data)

    def post(self, request, *args, **kwargs):
        context = super(AgentManagementRelationship, self).get_context_data(**kwargs)
        params = {}
        permissions = {}
        permissions = check_permission_agent_management(self)
        permissions['CAN_SEARCH_RELATIONSHIP'] = self.check_membership(['CAN_SEARCH_RELATIONSHIP'])
        relationship_types = self._get_relationship_types()
        self.logger.info('========== start getting relationship ==========')
        agent_id = int(kwargs.get('agent_id'))
        list_relationship_type = request.POST.getlist('list_relationship_type')
        partner_role = request.POST.get('partner_role')
        relationship_partner_id = request.POST.get('relationship_partner_id')

        if list_relationship_type:
            list_relationship_type = [int(i) for i in list_relationship_type]
            params['relationship_type_ids'] = list_relationship_type
        if relationship_partner_id:
            relationship_partner_id = int(relationship_partner_id)
            if partner_role == '0':
                params['user_id'] = agent_id
            elif partner_role == '1':
                params['main_user_id'] = relationship_partner_id
                params['sub_user_id'] = agent_id
            elif partner_role == '2':
                params['main_user_id'] = agent_id
                params['sub_user_id'] = relationship_partner_id
        else:
            params['user_id'] = agent_id

        self.logger.info("Params: {} ".format(params))
        data, success, status_message = self._get_relationships(params=params)

        if success:
            relationships_list = data.get("relationships", [])
            relationships_list = [relationship for relationship in relationships_list if not relationship['is_deleted']]
            page = data.get("page", {})

            context = {
                'agent_id': agent_id,
                'permissions': permissions,
                'search_count': len(relationships_list),
                'relationships': relationships_list,
                'relationship_type_id': list_relationship_type,
                'relationship_types': relationship_types,
                'default_tab': 1,
                'partner_role': partner_role,
                'relationship_partner_id': relationship_partner_id or None,
            }

        self.logger.info('========== finish search relationship ==========')

        return render(request, self.template_name, context)




