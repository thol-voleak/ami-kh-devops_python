from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.api_logger import API_Logger
from django.contrib import messages
from web_admin import api_settings, setup_logger, RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin
from braces.views import GroupRequiredMixin

from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)

class AddRuleCondition(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    group_required = "CAN_CREATE_CAMPAIGN"
    login_url = 'web:permission_denied'
    raise_exception = False
    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = 'rule_configuration/add_condition.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AddRuleCondition, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start adding Condition ==========')
        context = super(AddRuleCondition, self).get_context_data(**kwargs)
        rule_id = context['rule_id']
        mechanic_id = context['mechanic_id']

        params = {
            'key_name': request.POST['detail_name'],
            'key_value_type': request.POST['key_value_type'],
            'key_value': request.POST['key_value'],
            'operator': request.POST['operator']
        }

        self.logger.info('========== Start adding Condition ==========')
        success, data, message = self.create_condition(rule_id, mechanic_id, {'filter_type': request.POST.get('condition_type')})
        self.logger.info('========== Finish adding Condition ==========')

        if not success:
            return self.render_add_condition_page(request, context, message, params)

        condition_id = data['id']

        self.logger.info('========== Start adding Comparison ==========')
        success, data, message = self.create_comparison(rule_id, mechanic_id, condition_id, params)
        self.logger.info('========== Finish adding Comparison ==========')

        if not success:
            return self.render_add_condition_page(request, context, message, params)

        if 'add_more_condition' in request.POST.keys():
            self.get_page_data(context)
            messages.success(request, 'Condition is successfully created')
            return render(request, self.template_name, context)

        if 'next' in request.POST.keys():
            return redirect('rule_configuration:add_action', rule_id=rule_id, mechanic_id=mechanic_id)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start showing Add Rule Condition page ==========')
        context = super(AddRuleCondition, self).get_context_data(**kwargs)

        self.get_page_data(context)
        self.logger.info('========== Finished showing Add Rule Condition page ==========')
        return context

    def get_data_type_list(self):
        success, status_code, data = RestFulClient.get(url=api_settings.GET_RULE_CONDITION_DATA_TYPE, loggers=self.logger, headers=self._get_headers())
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                               status_code=status_code)
        if success:
            return data
        else:
            return []

    def get_operations_list(self):
        success, status_code, data = RestFulClient.get(url=api_settings.GET_RULE_OPERATION_LIST,
                                                       loggers=self.logger, headers=self._get_headers())
        API_Logger.get_logging(loggers=self.logger, params={}, response=data,
                               status_code=status_code)
        if success:
            return data
        else:
            return []

    def create_condition(self, rule_id, mechanic_id, params):
        success, status_code, message, data = RestFulClient.post(
            url = api_settings.CREATE_CONDITION.format(rule_id=rule_id, mechanic_id=mechanic_id),
            headers=self._get_headers(),
            loggers=self.logger,
            params=params)

        API_Logger.post_logging(loggers=self.logger, params=params, response=data, status_code=status_code)

        return success, data, message

    def get_page_data(self, context):
        detail_names = ["id", "user_id", "user_type", "device_id", "device_description", "event_name", "order_id",
                        "ext_transaction_id", "payment_method_name", "payment_method_ref", "command_id", "service_name",
                        "service_id", "command_name", "service_command_id", "initiator_user_id", "initiator_user_type",
                        "initiator_sof_id", "initiator_sof_type_id", "payer_user_id", "payer_user_type",
                        "payer_user_ref_type", "payer_user_left_value", "payer_sof_id", "payer_sof_type_id",
                        "payee_user_id", "payee_user_type", "payee_user_ref_type", "payee_user_ref_value",
                        "payee_sof_id", "payee_sof_type_id", "currency", "ref_order_id", "amount", "fee", "bonus",
                        "settlement_amount", "product_name", "product_ref1", "product_ref2", "product_ref3",
                        "product_ref4", "product_ref5", "state", "status", "notification_status", "is_deleted",
                        "order_created_timestamp", "order_last_updated_timestamp", "created_client_id",
                        "executed_client_id", "created_timestamp", "register_timestamp", "description",
                        "login_timestamp", "client_id"]

        self.logger.info('========== Start getting key value type list ==========')
        data_type_list = self.get_data_type_list()
        self.logger.info('========== Finish getting key value type list ==========')

        self.logger.info('========== Start getting operator list ==========')
        operations = self.get_operations_list()
        self.logger.info('========== Finish getting operator list ==========')
        # convert operators list
        operations_map = {
            "<": 'Less Than', ">": 'More Than', "=": 'Equal to',
            "!=": 'Not Equal to', "<=": 'Less than or Equal to',
            ">=": 'More than or equal to'
        }
        converted_operators = []
        for operator in operations:
            operators = {
                'key': operator,
                'value': operations_map[operator] if operations_map[operator] else operator
            }
            converted_operators.append(operators)
        ops = {
            'detail_names': detail_names,
            'key_value_types': data_type_list,
            'operations': converted_operators
        }
        context.update(ops)

    def render_add_condition_page(self, request, context, message, params):
        context['error_msg'] = message
        context['selected_detail_name'] = params['key_name']
        context['selected_value_type'] = params['key_value_type']
        context['selected_operator'] = params['operator']
        context['input_key_value'] = params['key_value']
        self.get_page_data(context)
        return render(request, self.template_name, context)

    def create_comparison(self, rule_id, mechanic_id, condition_id, params):
        success, status_code, message, data = RestFulClient.post(
            url=api_settings.CREATE_COMPARISON.format(rule_id=rule_id, mechanic_id=mechanic_id, condition_id=condition_id),
            headers=self._get_headers(),
            loggers=self.logger,
            params=params)

        API_Logger.post_logging(loggers=self.logger, params=params, response=data, status_code=status_code)

        return success, data, message




