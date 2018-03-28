from braces.views import GroupRequiredMixin
from web_admin import api_settings, setup_logger
from django.views.generic.base import TemplateView
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from django.shortcuts import redirect, render
from web_admin.restful_client import RestFulClient
from web_admin.api_logger import API_Logger
from web_admin.get_header_mixins import GetHeaderMixin
from django.contrib import messages
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

    def get(self, request, *args, **kwargs):
        context = super(AgentManagementProduct, self).get_context_data(**kwargs)
        self.logger.info('========== Start getting product portfolio ==========')
        body = {}
        body['user_id'] = int(context['agent_id'])

        permissions = {}
        permissions['CAN_ACCESS_RELATIONSHIP_TAB'] = self.check_membership(['CAN_ACCESS_RELATIONSHIP_TAB'])
        permissions['CAN_ACCESS_SUMMARY_TAB'] = self.check_membership(['CAN_ACCESS_SUMMARY_TAB'])

        context.update(
            {'agent_id': int(context['agent_id']),
             'permissions': permissions
             })

        applicable_categories, applied_category = _create_product_relation(self, int(context['agent_id']))
        context.update({
            'applicable_categories': applicable_categories,
        })
        self.logger.info('========== Finish getting product portfolio ==========')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = super(AgentManagementProduct, self).get_context_data(**kwargs)
        agent_id = int(context['agent_id'])
        self.logger.info('========== Start updating relation between product and agent ==========')
        old_checked_product_id_list = request.POST.getlist('old-selected-product-list')
        new_checked_product_id_list= request.POST.getlist('checkbox_product')

        #convert string list to int list
        old_checked_product_id_list = list(map(int, old_checked_product_id_list))
        new_checked_product_id_list = list(map(int, new_checked_product_id_list))

        newly_added_product = [product_id for product_id in new_checked_product_id_list if product_id not in old_checked_product_id_list]
        newly_deleted_product = [product_id for product_id in old_checked_product_id_list if product_id not in new_checked_product_id_list]
        is_all_success = True
        if newly_added_product:
            for product_id in newly_added_product:
                self.logger.info('========== Start adding relation between product and agent ==========')
                success = self.add_product_agent_relation({'product_id': product_id, 'agent_id': agent_id})
                is_all_success = is_all_success and success
                self.logger.info('========== Finish adding relation between product and agent ==========')

        if newly_deleted_product:
            for product_id in newly_deleted_product:
                self.logger.info('========== Start get product - agent relation ==========')
                relation_id = self.get_relation_id_of_product({'product_id': product_id, 'agent_id': agent_id})
                self.logger.info('========== Finished get product - agent relation ==========')
                if relation_id:
                    self.logger.info('========== Start deleting relation between product and agent ==========')
                    success = self.delete_product_agent_relation(relation_id)
                    is_all_success = is_all_success and success
                    self.logger.info('========== Finish deleting relation between product and agent ==========')

        self.logger.info('========== Finish updating relation between product and agent ==========')
        if is_all_success:
            messages.success(request, "Saved Successfully")
        return redirect("agents:agent_management_product", agent_id=agent_id)

    def add_product_agent_relation(self, body_request):
        url = api_settings.CREATE_PRODUCT_AGENT_RELATION

        is_success, status_code, status_message, data = RestFulClient.post(url,
                                                                           headers=self._get_headers(),
                                                                           params=body_request, loggers=self.logger)
        API_Logger.post_logging(loggers=self.logger, params=body_request, response=data,
                                status_code=status_code)
        return is_success

    def delete_product_agent_relation(self, relation_id):
        url = api_settings.DELETE_PRODUCT_AGENT_RELATION.format(relation_id=relation_id)

        is_success, status_code, data = RestFulClient.delete(url,
                                                             headers=self._get_headers(),
                                                             params={}, loggers=self.logger)
        self.logger.info("Params: {} ".format({}))
        API_Logger.delete_logging(loggers=self.logger, status_code=status_code)
        return is_success

    def get_relation_id_of_product(self, body_request):
        is_success, status_code, status_message, data = RestFulClient.post(
            url=api_settings.GET_PRODUCT_AGENT_RELATION, headers=self._get_headers(), loggers=self.logger,
            params=body_request
        )
        API_Logger.post_logging(loggers=self.logger, params=body_request, response=data, status_code=status_code,
                                is_getting_list=False)
        if data['relations']:
            relation = data['relations'][0]
            return relation['id']





