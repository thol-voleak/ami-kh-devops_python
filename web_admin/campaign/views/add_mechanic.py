from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.api_logger import API_Logger
from django.contrib import messages
from web_admin.api_settings import CREATE_MECHANIC, CREATE_CONDITION, CREATE_COMPARISON, CREATE_REWARD, CREATE_LIMITATION
from web_admin import setup_logger, RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin
from braces.views import GroupRequiredMixin
from datetime import datetime
from campaign.models import terms_mapping
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
        operations = ["Less Than", "More Than", "Equal to", "Not Equal to", "Less than or Equal to", "More than or Equal to"]
        freetext_ops = ["Equal to", "Not Equal to"]

        key_value_types = ["Numeric", "Freetext", "Timestamp"]
        filter_ops = ["Equal to", "Not Equal to"]
        filter_key_value_types = ["Numeric", "Timestamp"]

        all_terms = list(terms_mapping.objects.all())
        detail_names = self._filter_detail_names(all_terms)
        trigger = self._filter_trigger(all_terms)

        ops = {
            'operations': operations,
            'key_value_types': key_value_types,
            'detail_names': detail_names,
            'trigger': trigger,
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
            message = 'Required Field. Start date or time cannot be after end date and time. Date and Time cannot be in the past'
            context['border_color'] = 'red'
            return self.render_add_page(request, context, message)

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
            message = 'Required Field. Start date or time cannot be after end date and time. Date and Time cannot be in the past'
            context['border_color'] = 'red'
            return self.render_add_page(request, context, message, start_date, end_date)

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

        if not success:
            message = 'Required Field. Start date or time cannot be after end date and time. Date and Time cannot be in the past'
            return self.render_add_page(request, context, message, start_date, end_date)

        mechanic_id = data['id']
        operations_map = {
            "Less Than": '<', "More Than": '>', "Equal to": '=',
            "Not Equal to": '!=', "Less than or Equal to": '<=',
            "More than or Equal to": '>='
        }
        kv_type_map = {
            "Numeric": "numeric", "Freetext": "text", "Timestamp": "timestamp"
        }

        counter = request.POST.get('condition_counter') or 1
        for i in range(int(counter)):
            self.logger.info('========== Start adding Condition ==========')
            suffix = '' if i == 0 else str(i+1)
            condition_type = 'condition_type' + suffix
            key_value_type = 'key_value_type' + suffix
            detail_name = 'detail_name' + suffix
            operator = 'operator' + suffix
            key_value = 'key_value' + suffix

            if not request.POST.get(key_value):
                continue

            params = {'filter_type': request.POST.get(condition_type)}
            success, data, message = self.create_condition(campaign_id, mechanic_id, params)
            self.logger.info('========== Finish adding Condition ==========')
            if not success:
                return self.render_add_page(request, context, message, start_date, end_date)

            condition_id = data['id']

            self.logger.info('========== Start adding Comparison ==========')

            params = {
                'key_name': request.POST.get(detail_name),
                'key_value_type': kv_type_map[request.POST.get(key_value_type)],
                'operator': operations_map[request.POST.get(operator)],
                'key_value': request.POST.get(key_value),
            }
            success, data, message = self.create_comparison(campaign_id, mechanic_id, condition_id, params)
            self.logger.info('========== Finish adding Comparison ==========')
            if not success:
                return self.render_add_page(request, context, message, start_date, end_date)

        # add reward
        self.logger.info('========== Start adding Reward ==========')
        params = {
            'action_type_id':1,
            'data':[
                {
                    'key_name':'product_service_id',
                    'key_value': request.POST.get('product_service_id'),
                    'key_value_type':'numeric'
                },
                {
                    'key_name': 'payer_user.user_id',
                    'key_value': request.POST.get('payer_id'),
                    'key_value_type': 'numeric'
                },
                {
                    'key_name': 'payer_user.user_type',
                    'key_value': 'agent',
                    'key_value_type': 'text'
                },
                {
                    'key_name': 'payer_user.sof.id',
                    'key_value': request.POST.get('payer_sof_id'),
                    'key_value_type': 'numeric'
                },
                {
                    'key_name': 'payer_user.sof.type_id',
                    'key_value': '2',
                    'key_value_type': 'numeric'
                },
                {
                    'key_name': 'payee_user.user_id',
                    'key_value': request.POST.get('give_reward_to'),
                    'key_value_type': 'numeric'
                },
                {
                    'key_name': 'payee_user.user_type',
                    'key_value': request.POST.get('reward_recipient'),
                    'key_value_type': 'text'
                },
                {
                    'key_name': 'amount',
                    'key_value': request.POST.get('amount'),
                    'key_value_type': 'numeric'
                }
            ]
        }
        if request.POST.get('give_reward_to') != '@@user_id@@' :
            params['data'].append({
                        'key_name': 'paid_amount',
                        'key_value': "@@amount@@",
                        'key_value_type': "numeric"
                    })
        success, data, message = self.create_reward(campaign_id, mechanic_id, params)
        action_id = data.get("id", '')
        self.logger.info('========== Finish adding Reward ==========')

        if not success:
            return self.render_add_page(request, context, message, start_date, end_date)

        # add limitation
        self.logger.info('========== Start adding Limitation ==========')
        limit_to = request.POST.get('limit_to')
        limit_to = int(limit_to)
        params = {
            "limit_type": request.POST.get('limitation_type'),
            "value": limit_to,
            "filters": [
                {
                    'key_name': 'payee_user.user_type',
                    'key_value': request.POST.get('reward_recipient'),
                    'key_value_type': 'text',
                    "operator": "="
                },
                {
                    'key_name': 'payee_user.user_id',
                    'key_value': request.POST.get('give_reward_to'),
                    'key_value_type': 'numeric',
                    "operator": "="
                }
            ]
        }

        success, data, message = self.create_limitation(campaign_id, mechanic_id, action_id, params)

        self.logger.info('========== Finish adding Limitation ==========')

        if success:
            messages.success(request, 'Mechanic Added')
            return redirect('campaign:campaign_detail', campaign_id=campaign_id)

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

    def render_add_page(self, request, context, message, start_date=None, end_date=None):
        context['error_msg'] = message
        if start_date and end_date:
            context['dtp_start_date'] = start_date.strftime('%Y-%m-%d')
            context['dtp_end_date'] = end_date.strftime('%Y-%m-%d')
        operations = ["Less Than", "More Than", "Equal to", "Not Equal to",
                      "Less than or Equal to",
                      "More than or Equal to"]
        freetext_ops = ["Equal to", "Not Equal to"]
        key_value_types = ["Numeric", "Freetext", "Timestamp"]
        filter_ops = ["Equal to", "Not Equal to"]
        filter_key_value_types = ["Numeric", "Timestamp"]

        all_terms = list(terms_mapping.objects.all())
        detail_names = self._filter_detail_names(all_terms)
        trigger = self._filter_trigger(all_terms)

        context['operations'] = operations
        context['key_value_types'] = key_value_types
        context['detail_names'] = detail_names
        context['trigger'] = trigger
        context['freetext_ops'] = freetext_ops
        context['filter_ops'] = filter_ops
        context['filter_key_value_types'] = filter_key_value_types
        return render(request, self.template_name, context)

    def create_reward(self, campaign_id, mechanic_id, params):
        success, status_code, message, data = RestFulClient.post(
            url=CREATE_REWARD.format(rule_id=campaign_id, mechanic_id=mechanic_id),
            headers=self._get_headers(),
            loggers=self.logger,
            params=params)

        API_Logger.post_logging(loggers=self.logger, params=params, response=data, status_code=status_code)

        return success, data, message

    def create_limitation(self, campaign_id, mechanic_id, action_id, params):
        success, status_code, message, data = RestFulClient.post(
            url=CREATE_LIMITATION.format(rule_id=campaign_id, mechanic_id=mechanic_id, action_id=action_id),
            headers=self._get_headers(),
            loggers=self.logger,
            params=params)

        API_Logger.post_logging(loggers=self.logger, params=params, response=data, status_code=status_code)

        return success, data, message

    def _filter_detail_names(self, data):
        filtered = [v for v in data if (v.term != 'register_customer') and (v.term != 'executed_order') and (v.term != 'login')]
        return filtered

    def _filter_trigger(self, data):
        filtered = [v for v in data if ((v.term == 'register_customer') or (v.term == 'executed_order') or (v.term == 'login'))]
        return filtered