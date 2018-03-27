from braces.views import GroupRequiredMixin
from web_admin import api_settings, setup_logger
from django.views.generic.base import TemplateView
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from django.shortcuts import redirect, render
from web_admin.restful_client import RestFulClient
from web_admin.api_logger import API_Logger
from web_admin.get_header_mixins import GetHeaderMixin
from agents.utils import _create_product_relation
import logging

logger = logging.getLogger(__name__)
logging.captureWarnings(True)


class AgentManagementProduct(GroupRequiredMixin, TemplateView, GetHeaderMixin):

    template_name = "agents/management_product.html"
    group_required = "CAN_VIEW_PROFILE_MANAGEMENT"
    login_url = 'web:permission_denied'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AgentManagementProduct, self).dispatch(request, *args, **kwargs)

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
        return super(AgentManagementProduct, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(AgentManagementProduct, self).get_context_data(**kwargs)
        self.logger.info('========== Start getting product portfolio ==========')
        body = {}
        body['user_id'] = int(context['agent_id'])

        permissions = {}
        permissions['CAN_ACCESS_RELATIONSHIP_TAB'] = self.check_membership(['CAN_ACCESS_RELATIONSHIP_TAB'])
        permissions['CAN_ACCESS_SUMMARY_TAB'] = self.check_membership(['CAN_ACCESS_SUMMARY_TAB'])
        if permissions['CAN_ACCESS_SUMMARY_TAB']:
            pass
        elif permissions['CAN_ACCESS_RELATIONSHIP_TAB']:
            return redirect('agents:agent_management_relationship',agent_id=int(context['agent_id']))

        context.update(
            {'agent_id': int(context['agent_id']),
             'permissions': permissions
             })

        applicable_categories = _create_product_relation(self, int(context['agent_id']))
        context.update({
            'applicable_categories': applicable_categories,
        })
        self.logger.info('========== Finish getting product portfolio ==========')
        return render(request, self.template_name, context)



