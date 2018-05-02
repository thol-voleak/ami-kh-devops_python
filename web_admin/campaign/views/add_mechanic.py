from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.api_logger import API_Logger
from django.contrib import messages
from web_admin.api_settings import CREATE_MECHANIC, CREATE_CONDITION, CREATE_COMPARISON, CREATE_REWARD, CREATE_LIMITATION, CREATE_FILTER, CREATE_RESET_FILTER
from web_admin import setup_logger, RestFulClient
from web_admin.restful_helper import RestfulHelper
from web_admin.get_header_mixins import GetHeaderMixin
from braces.views import GroupRequiredMixin
from datetime import datetime
from campaign.models import terms_mapping
from django.views.generic.base import TemplateView
from django.http import JsonResponse

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
        operations = ["Equal to", "Not Equal to", "Less Than", "More Than", "Less than or Equal to", "More than or Equal to"]
        freetext_ops = ["Equal to", "Not Equal to", "Contains"]

        key_value_types = ["Numeric", "Freetext", "Timestamp"]
        filter_ops = ["Equal to", "Not Equal to"]
        filter_key_value_types = ["Numeric", "Timestamp"]
        sum_of_operators = ["Equal to", "Not Equal to", "Less than or Equal to", "More than or Equal to"]
        count_of_operators = ["Equal to",  "Less Than", "More Than", "More than or Equal to", "Less than or Equal to"]
        count_consecutive_of_operators = ["Equal to", "More than or Equal to"]
        sum_key_name = [{
                'value': 'amount',
                'text': 'Amount'
            }, {
                'value': 'fee',
                'text': 'Fee'
            },{
                'value': 'bonus',
                'text': 'Bonus'
            },{
                'value': 'settlement_amount',
                'text': 'Settlement Amount'
            }]
        all_terms = list(terms_mapping.objects.all())
        detail_names = self._filter_detail_names(all_terms)
        username = {'term': 'username', 'description': ''}
        is_login_success = {'term': 'is_login_success', 'description': ''}
        detail_names.extend((username, is_login_success))
        trigger = self._filter_trigger(all_terms)

        ops = {
            'operations': operations,
            'key_value_types': key_value_types,
            'detail_names': detail_names,
            'trigger': trigger,
            'freetext_ops': freetext_ops,
            'filter_ops': filter_ops,
            'filter_key_value_types': filter_key_value_types,
            'sum_of_operators': sum_of_operators,
            'count_of_operators': count_of_operators,
            'count_consecutive_of_operators': count_consecutive_of_operators,
            'sum_key_name': sum_key_name
        }

        context.update(ops)
        self.logger.info('========== Finished showing Add Mechanic page ==========')
        return context

    def post(self, request, *args, **kwargs):
        context = super(AddMechanic, self).get_context_data(**kwargs)
        campaign_id = context['campaign_id']
        input_start_date = request.POST.get('dtp_start_date')
        input_end_date = request.POST.get('dtp_end_date')
        input_start_time = request.POST.get('dtp_start_time')
        input_end_time = request.POST.get('dtp_end_time')

        if input_start_date is "" or input_end_date is "" or input_start_time is "" or input_end_time is "":
            message = 'Required Field. Start date or time cannot be after end date and time. Date and Time cannot be in the past'
            return JsonResponse({"status": 4, "msg": message})

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
            return JsonResponse({"status": 4, "msg": message})

        param_start_date = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        param_end_date = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        params = {
            "event_name": request.POST.get('trigger'),
            "start_timestamp": param_start_date,
            "end_timestamp": param_end_date
        }

        add_mechanic_url = CREATE_MECHANIC.format(rule_id=campaign_id)
        success, status_code, message, data = RestfulHelper.send("POST", add_mechanic_url, params, self.request,
                                                                           " adding Mechanic")
        if not success:
            message = 'Required Field. Start date or time cannot be after end date and time. Date and Time cannot be in the past'
            return JsonResponse({"status": 4, "msg": message})

        mechanic_id = data['id']
        operations_map = {
            "Less Than": '<', "More Than": '>', "Equal to": '=',
            "Not Equal to": '!=', "Less than or Equal to": '<=',
            "More than or Equal to": '>=',
            "Contains": "contains",
        }
        kv_type_map = {
            "Numeric": "numeric", "Freetext": "text", "Timestamp": "timestamp"
        }

        counter = request.POST.get('condition_counter') or 1
        for i in range(1, int(counter) + 1):
            suffix = str(i)
            filter_counter = request.POST.get('filter_count_' + suffix) or 1
            condition_type = request.POST.get('condition_type_' + suffix)
            sum_key_name = request.POST.get('sum_key_name_' + suffix)
            sum_operator = request.POST.get('sum_operator_' + suffix)
            sum_key_value = request.POST.get('sum_key_value_' + suffix)

            if condition_type == 'event_detail':
                params = {'filter_type': condition_type}
                success, data, message = self.create_condition(campaign_id, mechanic_id, params)
                if not success:
                    return JsonResponse({"status": 3, "msg": message})

                condition_id = data['id']
                key_value_type = 'key_value_type_' + suffix
                detail_name = 'detail_name_' + suffix
                operator = 'operator_' + suffix
                key_value = 'key_value_' + suffix

                if not request.POST.get(key_value):
                    continue


                params = {
                    'key_name': request.POST.get(detail_name),
                    'key_value_type': kv_type_map[request.POST.get(key_value_type)],
                    'operator': operations_map[request.POST.get(operator)],
                    'key_value': request.POST.get(key_value),
                }
                success, data, message = self.create_comparison(campaign_id, mechanic_id, condition_id, params)
                if not success:
                    return JsonResponse({"status": 3, "msg": message})

            elif condition_type == 'sum_of':
                # condition_type == 'sum_of'
                params = {'filter_type': condition_type, 'sum_key_name': sum_key_name}
                success, data, message = self.create_condition(campaign_id, mechanic_id, params)
                if not success:
                    return JsonResponse({"status": 3, "msg": message})

                condition_id = data['id']

                params = {
                    'key_name': 'sum_result',
                    'key_value_type': 'numeric',
                    'operator': operations_map[sum_operator],
                    'key_value': sum_key_value,
                }
                success, data, message = self.create_comparison(campaign_id, mechanic_id, condition_id, params)
                if not success:
                    return JsonResponse({"status": 3, "msg": message})

                for i in range(1, int(filter_counter) + 1):
                    prefix = str(i)
                    key_value_type = prefix + '_key_value_type_' + suffix
                    detail_name = prefix + '_detail_name_' + suffix
                    operator = prefix + '_operator_' + suffix
                    key_value = prefix + '_key_value_' + suffix

                    if not request.POST.get(key_value):
                        continue
                    params = {
                        'key_name': request.POST.get(detail_name),
                        'key_value_type': kv_type_map[request.POST.get(key_value_type)],
                        'operator': operations_map[request.POST.get(operator)],
                        'key_value': request.POST.get(key_value),
                    }
                    success, data, message = self.create_filter(campaign_id, mechanic_id, condition_id, params)
                    if not success:
                        return JsonResponse({"status": 3, "msg": message})
            elif condition_type == 'count_of':
                count_count_of = request.POST.get('count_' + suffix)
                count_of_operator = request.POST.get('count_of_operator_' + suffix)
                count_of_filter_counter = request.POST.get('filter_count_of_count_' + suffix) or 0
                within_type = request.POST.get('within_' + suffix)
                event_name_filter_counter = request.POST.get('event_name_' + suffix)
                success, condition_id, message = self.create_common_count_of_condition(request, suffix, campaign_id, mechanic_id,
                                                                condition_type, operations_map, count_of_operator,
                                                                count_count_of,
                                                                within_type, event_name_filter_counter,
                                                                count_of_filter_counter,
                                                                kv_type_map)
                if not success:
                    return JsonResponse({"status": 3, "msg": message})
            else:
                # condition_type == 'count_consecutive_of'
                count_count_of = request.POST.get('consecutive_count_' + suffix)
                count_of_operator = request.POST.get('consecutive_count_of_operator_' + suffix)
                count_of_filter_counter = request.POST.get('filter_count_of_count_' + suffix) or 0
                count_of_reset_filter_counter = request.POST.get('reset_filter_count_of_count_' + suffix) or 0
                within_type = request.POST.get('consecutive_within_' + suffix)
                event_name_filter_counter = request.POST.get('consecutive_event_name_' + suffix)
                success, condition_id, message = self.create_common_count_of_condition(request, suffix, campaign_id, mechanic_id,
                                                     condition_type, operations_map, count_of_operator, count_count_of,
                                                     within_type, event_name_filter_counter, count_of_filter_counter,
                                                     kv_type_map)
                if not success:
                    return JsonResponse({"status": 3, "msg": message})
                # consecutive key detail
                consecutive_key_value_type = request.POST.get('consecutive_key_value_type_' + suffix)
                consecutive_detail_name = request.POST.get('consecutive_detail_name_' + suffix)
                consecutive_operator = request.POST.get('consecutive_operator_' + suffix)
                consecutive_key_value = request.POST.get('consecutive_key_value_' +suffix)
                condition_reset_event = request.POST.get('condition_reset_event_' + suffix)
                params = {
                    'key_name': consecutive_detail_name,
                    'key_value_type': kv_type_map[consecutive_key_value_type],
                    'operator': operations_map[consecutive_operator],
                    'key_value': consecutive_key_value,
                    'is_consecutive_key': True
                }
                success, data, message = self.create_filter(campaign_id, mechanic_id, condition_id, params)

                # condition reset value
                params = {
                    'key_name': 'event_name',
                    'key_value_type': 'text',
                    'operator': '=',
                    'key_value': condition_reset_event,
                }
                success, data, message = self.create_reset_filter(campaign_id, mechanic_id, condition_id, params)
                for i in range(1, int(count_of_reset_filter_counter) + 1):
                    prefix = str(i)
                    key_value_type = prefix + '_reset_filter_key_value_type_' + suffix
                    detail_name = prefix + '_reset_filter_detail_name_' + suffix
                    operator = prefix + '_reset_filter_operator_' + suffix
                    key_value = prefix + '_reset_filter_key_value_' + suffix

                    if not request.POST.get(key_value):
                        continue
                    params = {
                        'key_name': request.POST.get(detail_name),
                        'key_value_type': kv_type_map[request.POST.get(key_value_type)],
                        'operator': operations_map[request.POST.get(operator)],
                        'key_value': request.POST.get(key_value),
                    }
                    success, data, message = self.create_reset_filter(campaign_id, mechanic_id, condition_id, params)
        # add reward

        reward_type = request.POST.get('reward_type')
        if reward_type == 'fixed_cashback':
            params = {
                'action_type_id':1,
                'user_id': request.POST.get('give_reward_to'),
                'user_type': request.POST.get('reward_recipient'),
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
        elif reward_type == 'send_notification':
            detail_type_mapping = {
                "text": ["id", "user_type", "device_id", "device_description",
                         "event_name", "order_id", "ext_transaction_id",
                         "payment_method_name", "payment_method_ref",
                         "service_name", "command_name", "initiator_user_type",
                         "payer_user_type", "payer_user_ref_type",
                         "payer_user_ref_value", "payee_user_type",
                         "payee_user_ref_type", "payee_user_ref_value",
                         "currency", "ref_order_id", "product_name",
                         "product_ref1", "product_ref2", "product_ref3",
                         "product_ref4", "product_ref5", "state", "is_deleted",
                         "created_client_id", "executed_client_id",
                         "description", "client_id", "bank_account_name",
                         "ext_bank_reference", "sof_type", "channel"],
                "numeric": ["user_id", "command_id", "service_id",
                            "service_command_id", "initiator_user_id",
                            "initiator_sof_id", "initiator_sof_type_id",
                            "payer_user_id", "payer_sof_id",
                            "payer_sof_type_id", "payee_user_id",
                            "payee_sof_id", "payee_sof_type_id", "amount",
                            "fee", "bonus", "settlement_amount", "status",
                            "notification_status", "bank_id", "sof_id"],
                "timestamp": ["order_created_timestamp",
                              "order_last_updated_timestamp",
                              "created_timestamp", "register_timestamp",
                              "login_timestamp", "event_created_timestamp"]
            }

            params = {
                "action_type_id": 2,
                'user_id': request.POST.get('give_reward_to'),
                'user_type': request.POST.get('reward_recipient'),
                "data": [
                    {
                        "key_name": "notification_url",
                        "key_value": request.POST.get('send_to'),
                        "key_value_type": "text"
                    }
                ]
            }
            counter = request.POST.get('data_counter') or 1
            for i in range(int(counter)):
                suffix = '' if i == 0 else str(i + 1)
                reward_data_type = 'reward_data_type' + suffix
                data_type = request.POST.get(reward_data_type)
                if not data_type:
                    continue
                if data_type == 'from_database':
                    reward_detail_name = 'reward_detail_name' + suffix
                    detail_name = request.POST.get(reward_detail_name)
                    reward_key_value_type = ''
                    for type in detail_type_mapping:
                        if detail_name in detail_type_mapping[type]:
                            reward_key_value_type = type
                            break
                    if not reward_key_value_type:
                        self.logger.error('>>>>>>>>>> Cannot find detail type for [{}] from detail mapping <<<<<<<<<<'.format(detail_name))

                    params['data'].append({
                        "key_name": detail_name,
                        "key_value": '@@' + detail_name + '@@',
                        "key_value_type": reward_key_value_type
                    })
                elif data_type == 'user_defined':
                    reward_key_name = 'reward_key_name' + suffix
                    reward_key_value_type = 'reward_key_value_type' + suffix
                    reward_key_value = 'reward_key_value' + suffix
                    params['data'].append({
                        "key_name": request.POST.get(reward_key_name),
                        "key_value": request.POST.get(reward_key_value),
                        "key_value_type": kv_type_map[request.POST.get(reward_key_value_type)]
                    })
        elif reward_type == 'suspend_account':
            params = {
                "action_type_id": 4,
                'user_id':  request.POST.get('give_reward_to'),
                'user_type': request.POST.get('reward_recipient'),
                "data": [
                    {
                        'key_name': 'user_id',
                        'key_value': request.POST.get('give_reward_to'),
                        'key_value_type': 'numeric'
                    },
                    {
                        'key_name': 'user_type',
                        'key_value': request.POST.get('reward_recipient'),
                        'key_value_type': 'text'
                    },
                ]
            }

        success, data, message = self.create_reward(campaign_id, mechanic_id, params)
        action_id = data.get("id", '')

        if not success:
            return JsonResponse({"status": 3, "msg": message})

        # add limitation
        limit_to = request.POST.get('limit_to')
        limit_to = int(limit_to)
        params = {
            "limit_type": request.POST.get('limitation_type'),
            "value": limit_to,
            "filters": [
                {
                    'key_name': 'user_type',
                    'key_value': request.POST.get('reward_recipient'),
                    'key_value_type': 'text',
                    "operator": "="
                },
                {
                    'key_name': 'user_id',
                    'key_value': request.POST.get('give_reward_to'),
                    'key_value_type': 'numeric',
                    "operator": "="
                }
            ]
        }

        success, data, message = self.create_limitation(campaign_id, mechanic_id, action_id, params)
        if success:
            messages.success(request, 'Mechanic Added')
            return JsonResponse({"status": 2, "msg": message})

    def create_condition(self, campaign_id, mechanic_id, params):
        add_condition_url = CREATE_CONDITION.format(rule_id=campaign_id, mechanic_id=mechanic_id)
        success, status_code, message, data = RestfulHelper.send("POST", add_condition_url, params, self.request,
                                                                 " creating condition")
        return success, data, message

    def create_comparison(self, campaign_id, mechanic_id, condition_id, params):
        add_comparison_url = CREATE_COMPARISON.format(rule_id=campaign_id, mechanic_id=mechanic_id, condition_id=condition_id)
        success, status_code, message, data = RestfulHelper.send("POST", add_comparison_url, params, self.request,
                                                                 " creating comparison")

        return success, data, message

    def create_filter(self, campaign_id, mechanic_id, condition_id, params):
        add_filter_url = CREATE_FILTER.format(rule_id=campaign_id, mechanic_id=mechanic_id, condition_id=condition_id)
        success, status_code, message, data = RestfulHelper.send("POST", add_filter_url, params, self.request,
                                                                 " creating filter")
        return success, data, message

    def create_reset_filter(self, campaign_id, mechanic_id, condition_id, params):
        add_reset_filter_url = CREATE_RESET_FILTER.format(rule_id=campaign_id, mechanic_id=mechanic_id, condition_id=condition_id)
        success, status_code, message, data = RestfulHelper.send("POST", add_reset_filter_url, params, self.request,
                                                                 " creating reset filter")
        return success, data, message

    def create_reward(self, campaign_id, mechanic_id, params):
        add_reward_url = CREATE_REWARD.format(rule_id=campaign_id, mechanic_id=mechanic_id)
        success, status_code, message, data = RestfulHelper.send("POST", add_reward_url, params, self.request,
                                                                 " creating reward")
        return success, data, message

    def create_limitation(self, campaign_id, mechanic_id, action_id, params):
        add_limitation_url = CREATE_LIMITATION.format(rule_id=campaign_id, mechanic_id=mechanic_id, action_id=action_id)
        success, status_code, message, data = RestfulHelper.send("POST", add_limitation_url, params, self.request,
                                                                 " creating Limitation")
        return success, data, message

    def _filter_detail_names(self, data):
        filtered = [v for v in data if
                    (v.term != 'register_customer') and (v.term != 'executed_order') and (v.term != 'login')]
        return filtered

    def _filter_trigger(self, data):
        filtered = [v for v in data if
                    ((v.term == 'register_customer') or (v.term == 'executed_order') or (v.term == 'login'))]
        link_bank = {'term': 'created_sof', 'description': 'Link Bank'}
        created_order = {'term': 'create_order', 'description': 'Create Order'}
        limit_reached = {'term': 'limit_reached', 'description': 'Limit Reached'}
        filtered.extend([link_bank, created_order, limit_reached])
        return filtered

    def create_common_count_of_condition(self, request, suffix, campaign_id, mechanic_id, condition_type, operations_map, count_of_operator, count_count_of, within_type, event_name_filter_counter, count_of_filter_counter, kv_type_map):
        params = {'filter_type': condition_type}
        success, data, message = self.create_condition(campaign_id, mechanic_id, params)
        if not success:
            return success, None, message

        condition_id = data['id']

        params = {
            'key_name': 'count_result',
            'key_value_type': 'numeric',
            'operator': operations_map[count_of_operator],
            'key_value': count_count_of,
        }
        success, data, message = self.create_comparison(campaign_id, mechanic_id, condition_id, params)
        if not success:
            return success, None, message
        if within_type == 'timebox':
            if condition_type == 'count_of':
                timebox_minute = request.POST.get('txt_timebox_' + suffix)
            else:
                timebox_minute = request.POST.get('consecutive_txt_timebox_' + suffix)
            params = {
                'key_name': 'event_created_timestamp',
                'key_value_type': 'timestamp',
                'operator': '>=',
                'key_value': "@@@@event_created_timestamp@@-minutes(" + timebox_minute + ")@@",
            }
            success, data, message = self.create_filter(campaign_id, mechanic_id, condition_id, params)
            if not success:
                return success, None, message

            params = {
                'key_name': 'event_created_timestamp',
                'key_value_type': 'timestamp',
                'operator': '<=',
                'key_value': "@@event_created_timestamp@@",
            }
            success, data, message = self.create_filter(campaign_id, mechanic_id, condition_id, params)
            if not success:
                return success, None, message
        else:
            if condition_type == 'count_of':
                count_of_input_start_date = request.POST.get('within_from_' + suffix)
                count_of_input_end_date = request.POST.get('within_to_' + suffix)
                count_of_input_start_time = request.POST.get('within_from_time_' + suffix)
                count_of_input_end_time = request.POST.get('within_to_time_' + suffix)
            else:
                count_of_input_start_date = request.POST.get('consecutive_within_from_' + suffix)
                count_of_input_end_date = request.POST.get('consecutive_within_to_' + suffix)
                count_of_input_start_time = request.POST.get('consecutive_within_from_time_' + suffix)
                count_of_input_end_time = request.POST.get('consecutive_within_to_time_' + suffix)
            if not count_of_input_start_time:
                count_of_input_start_time = '00:00'
            if not count_of_input_end_time:
                count_of_input_end_time = '00:00'
            count_of_start_hour = int(count_of_input_start_time[0:2])
            count_of_start_minute = int(count_of_input_start_time[-2:])
            count_of_end_hour = int(count_of_input_end_time[0:2])
            count_of_end_minute = int(count_of_input_end_time[-2:])
            count_of_start_date = datetime.strptime(count_of_input_start_date, "%Y-%m-%d")
            count_of_start_date = count_of_start_date.replace(hour=count_of_start_hour,
                                                              minute=count_of_start_minute, second=0)
            count_of_end_date = datetime.strptime(count_of_input_end_date, "%Y-%m-%d")
            count_of_end_date = count_of_end_date.replace(hour=count_of_end_hour,
                                                          minute=count_of_end_minute, second=0)

            count_of_param_start_date = count_of_start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            count_of_param_end_date = count_of_end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            params = {
                'key_name': 'event_created_timestamp',
                'key_value_type': 'timestamp',
                'operator': ">=",
                'key_value': count_of_param_start_date,
            }
            success, data, message = self.create_filter(campaign_id, mechanic_id, condition_id, params)
            if not success:
                return success, None, message

            params = {
                'key_name': 'event_created_timestamp',
                'key_value_type': 'timestamp',
                'operator': "<=",
                'key_value': count_of_param_end_date,
            }
            success, data, message = self.create_filter(campaign_id, mechanic_id, condition_id, params)
            if not success:
                return success, None, message

        params = {
            'key_name': 'event_name',
            'key_value_type': 'text',
            'operator': "=",
            'key_value': event_name_filter_counter,
        }
        success, data, message = self.create_filter(campaign_id, mechanic_id, condition_id, params)
        if not success:
            return success, None, message
        for i in range(1, int(count_of_filter_counter) + 1):
            prefix = str(i)
            key_value_type = prefix + '_key_value_type_' + suffix
            detail_name = prefix + '_detail_name_' + suffix
            operator = prefix + '_operator_' + suffix
            key_value = prefix + '_key_value_' + suffix

            if not request.POST.get(key_value):
                continue
            params = {
                'key_name': request.POST.get(detail_name),
                'key_value_type': kv_type_map[request.POST.get(key_value_type)],
                'operator': operations_map[request.POST.get(operator)],
                'key_value': request.POST.get(key_value),
            }
            success, data, message = self.create_filter(campaign_id, mechanic_id, condition_id, params)
            if not success:
                return success, None, message
        success = True
        return success, condition_id, message

