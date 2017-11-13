from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.api_logger import API_Logger
from django.contrib import messages
from web_admin.api_settings import CREATE_MECHANIC, CREATE_CONDITION, CREATE_COMPARISON
from web_admin import setup_logger, RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin
from braces.views import GroupRequiredMixin
from datetime import datetime
from django.conf import settings
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class AddMechanic(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    group_required = "CAN_CREATE_CAMPAIGN"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "campaign/add_mechanic.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AddMechanic, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start showing Add Mechanic page ==========')
        context = super(AddMechanic, self).get_context_data(**kwargs)
        context['dtp_start_date'] = datetime.now().strftime("%Y-%m-%d")
        context['dtp_end_date'] = datetime.now().strftime("%Y-%m-%d")
        operations = ["Less Than", "More Than", "Equal to", "Not Equal to", "Less than or Equal to", "More than or equal to"]
        freetext_ops = ["Equal to", "Not Equal to"]

        key_value_types = ["Numeric", "Freetext", "Timestamp"]
        filter_ops = ["Equal to", "Not Equal to"]
        filter_key_value_types = ["Numeric", "Timestamp"]

        detail_names = ["id", "event_name", "created_timestamp", "user_id", "user_type", "device_id", "device_description", "event_timestamp", "order_id", "ext_transaction_id", "payment_method_name", "payment_method_ref", "service_id", "service_name", "command_id", "command_name", "service_command_id", "initiator_user_id", "initiator_user_type", "initiator_sof_id", "initiator_sof_type_id", "payer_user_id", "payer_user_type", "payer_user_ref_type", "payer_user_ref_value", "payer_sof_id", "payer_sof_type_id", "payee_user_id", "payee_user_type", "payee_user_ref_type", "payee_user_ref_value", "payee_sof_id", "payee_sof_type_id", "currency", "ref_order_id", "amount", "fee", "bonus", "settlement_amount", "product_name", "product_ref1", "product_ref2", "product_ref3", "product_ref4", "product_ref5", "state", "status", "notification_status", "is_deleted", "order_created_timestamp", "order_last_updated_timestamp", "created_client_id", "executed_client_id"]

        ops = {
            'operations': operations,
            'key_value_types': key_value_types,
            'detail_names': detail_names,
            'freetext_ops': freetext_ops,
            'filter_ops': filter_ops,
            'filter_key_value_types': filter_key_value_types,
        }

        context.update(ops)
        self.logger.info('========== Finished showing Add Mechanic page ==========')
        return context

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start adding Mechanic ==========')
        context = super(AddMechanic, self).get_context_data(**kwargs)
        campaign_id = context['campaign_id']
        input_start_date = request.POST.get('dtp_start_date')
        input_end_date = request.POST.get('dtp_end_date')
        input_start_time = request.POST.get('dtp_start_time')
        input_end_time = request.POST.get('dtp_end_time')

        if input_start_date is "" or input_end_date is "" or input_start_time is "" or input_end_time is "":
            context['error_msg'] = 'Start date or time cannot be after end date and time. Date and Time cannot be in the past'
            context['border_color'] = 'red'
            operations = ["Less Than", "More Than", "Equal to", "Not Equal to", "Less than or Equal to",
                          "More than or equal to"]
            freetext_ops = ["Equal to", "Not Equal to"]
            key_value_types = ["Numeric", "Freetext", "Timestamp"]
            filter_ops = ["Equal to", "Not Equal to"]
            filter_key_value_types = ["Numeric", "Timestamp"]
            detail_names = ["id", "event_name", "created_timestamp", "user_id", "user_type", "device_id",
                            "device_description", "event_timestamp", "order_id", "ext_transaction_id",
                            "payment_method_name", "payment_method_ref", "service_id", "service_name", "command_id",
                            "command_name", "service_command_id", "initiator_user_id", "initiator_user_type",
                            "initiator_sof_id", "initiator_sof_type_id", "payer_user_id", "payer_user_type",
                            "payer_user_ref_type", "payer_user_ref_value", "payer_sof_id", "payer_sof_type_id",
                            "payee_user_id", "payee_user_type", "payee_user_ref_type", "payee_user_ref_value",
                            "payee_sof_id", "payee_sof_type_id", "currency", "ref_order_id", "amount", "fee", "bonus",
                            "settlement_amount", "product_name", "product_ref1", "product_ref2", "product_ref3",
                            "product_ref4", "product_ref5", "state", "status", "notification_status", "is_deleted",
                            "order_created_timestamp", "order_last_updated_timestamp", "created_client_id",
                            "executed_client_id"]

            context['operations'] = operations
            context['key_value_types'] = key_value_types
            context['detail_names'] = detail_names
            context['freetext_ops'] = freetext_ops
            context['filter_ops'] = filter_ops
            context['filter_key_value_types'] = filter_key_value_types
            return render(request, self.template_name, context)

        start_hour = int(input_start_time[0:2])
        start_minute = int(input_start_time[-2:])
        end_hour = int(input_end_time[0:2])
        end_minute = int(input_end_time[-2:])
        start_date = datetime.strptime(input_start_date, "%Y-%m-%d")
        start_date = start_date.replace(hour=start_hour, minute=start_minute, second=0)
        end_date = datetime.strptime(input_end_date, "%Y-%m-%d")
        end_date = end_date.replace(hour=end_hour, minute=end_minute, second=0)
        current_date = datetime.now()

        if start_date > end_date or start_date < current_date or end_date < current_date:
            context['error_msg'] = 'Start date or time cannot be after end date and time. Date and Time cannot be in the past'
            context['dtp_start_date'] = start_date.strftime('%Y-%m-%d')
            context['dtp_end_date'] = end_date.strftime('%Y-%m-%d')
            context['border_color'] = 'red'
            return render(request, self.template_name, context)

        param_start_date = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        param_end_date = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        params = {
            "event_name": request.POST.get('trigger'),
            "start_timestamp": param_start_date,
            "end_timestamp": param_end_date
        }

        success, status_code, message, data = RestFulClient.post(
            url=CREATE_MECHANIC.format(rule_id=campaign_id),
            headers=self._get_headers(),
            loggers=self.logger,
            params=params)

        API_Logger.post_logging(loggers=self.logger, params=params, response=data, status_code=status_code)

        self.logger.info('========== Finish adding Mechanic ==========')
        if success:
            messages.success(request, 'A mechanic is created successfully')
        else:
            context['error_msg'] = message
            context['dtp_start_date'] = start_date.strftime('%Y-%m-%d')
            context['dtp_end_date'] = end_date.strftime('%Y-%m-%d')
            operations = ["Less Than", "More Than", "Equal to", "Not Equal to", "Less than or Equal to",
                          "More than or equal to"]
            freetext_ops = ["Equal to", "Not Equal to"]
            key_value_types = ["Numeric", "Freetext", "Timestamp"]
            filter_ops = ["Equal to", "Not Equal to"]
            filter_key_value_types = ["Numeric", "Timestamp"]
            detail_names = ["id", "event_name", "created_timestamp", "user_id", "user_type", "device_id",
                            "device_description", "event_timestamp", "order_id", "ext_transaction_id",
                            "payment_method_name", "payment_method_ref", "service_id", "service_name", "command_id",
                            "command_name", "service_command_id", "initiator_user_id", "initiator_user_type",
                            "initiator_sof_id", "initiator_sof_type_id", "payer_user_id", "payer_user_type",
                            "payer_user_ref_type", "payer_user_ref_value", "payer_sof_id", "payer_sof_type_id",
                            "payee_user_id", "payee_user_type", "payee_user_ref_type", "payee_user_ref_value",
                            "payee_sof_id", "payee_sof_type_id", "currency", "ref_order_id", "amount", "fee", "bonus",
                            "settlement_amount", "product_name", "product_ref1", "product_ref2", "product_ref3",
                            "product_ref4", "product_ref5", "state", "status", "notification_status", "is_deleted",
                            "order_created_timestamp", "order_last_updated_timestamp", "created_client_id",
                            "executed_client_id"]

            context['operations']= operations
            context['key_value_types']= key_value_types
            context['detail_names']= detail_names
            context['freetext_ops']= freetext_ops
            context['filter_ops']= filter_ops
            context['filter_key_value_types']= filter_key_value_types
            return render(request, self.template_name, context)

        self.logger.info('========== Start adding Condition ==========')
        mechanic_id = data['id']
        params = {'filter_type': request.POST.get('condition_type')}
        success, data, message = self.create_condition(campaign_id, mechanic_id, params)
        self.logger.info('========== Finish adding Condition ==========')
        if not success:
            return

        self.logger.info('========== Start adding Comparison ==========')
        condition_id = data['id']
        operations_map = {
            "Less Than": '<', "More Than": '>', "Equal to": '=',
            "Not Equal to": '!=', "Less than or Equal to": '<=',
            "More than or equal to": '>='
        }
        kv_type_map = {
            "Numeric": "numeric", "Freetext": "text", "Timestamp": "timestamp"
        }
        params = {
            'key_name': request.POST.get('detail_name'),
            'key_value_type': kv_type_map[request.POST.get('key_value_type')],
            'operator': operations_map[request.POST.get('operator')],
            'key_value': request.POST.get('key_value'),
        }
        success, data, message = self.create_comparison(campaign_id, mechanic_id, condition_id, params)
        self.logger.info('========== Finish adding Comparison ==========')
        if success:
            return redirect('campaign:campaign_detail',campaign_id=campaign_id)


    def create_condition(self, campaign_id, mechanic_id, params):
        success, status_code, message, data = RestFulClient.post(
            url=CREATE_CONDITION.format(rule_id=campaign_id, mechanic_id=mechanic_id),
            headers=self._get_headers(),
            loggers=self.logger,
            params=params)

        API_Logger.post_logging(loggers=self.logger, params=params, response=data, status_code=status_code)

        return success, data, message

    def create_comparison(self, campaign_id, mechanic_id, condition_id, params):
        success, status_code, message, data = RestFulClient.post(
            url=CREATE_COMPARISON.format(rule_id=campaign_id, mechanic_id=mechanic_id, condition_id=condition_id),
            headers=self._get_headers(),
            loggers=self.logger,
            params=params)

        API_Logger.post_logging(loggers=self.logger, params=params, response=data, status_code=status_code)

        return success, data, message

