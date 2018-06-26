from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.api_logger import API_Logger
from django.contrib import messages
from web_admin.api_settings import CREATE_MECHANIC, CREATE_CONDITION, CREATE_COMPARISON, CREATE_REWARD, CREATE_LIMITATION, CREATE_FILTER, CREATE_RESET_FILTER
from web_admin import setup_logger, RestFulClient, api_settings
from web_admin.restful_helper import RestfulHelper
from web_admin.get_header_mixins import GetHeaderMixin
from braces.views import GroupRequiredMixin
from datetime import datetime
from campaign.models import terms_mapping
from django.views.generic.base import TemplateView
from django.http import JsonResponse

import logging

logger = logging.getLogger(__name__)


class AddAction(TemplateView, GetHeaderMixin):
    template_name = "campaign/add_action.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AddAction, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start showing Add Action page ==========')
        context = super(AddAction, self).get_context_data(**kwargs)

        campaign_id = context['campaign_id']
        mechanic_id = context['mechanic_id']
        success, mechanic = self.get_mechanic(campaign_id, mechanic_id)

        key_value_types = ["Numeric", "Freetext", "Timestamp"]
        all_terms = list(terms_mapping.objects.all())
        detail_names = self._filter_detail_names(all_terms)
        username = {'term': 'username', 'description': ''}
        is_login_success = {'term': 'is_login_success', 'description': ''}
        is_suspend = {'term': 'is_suspend', 'description': ''}
        detail_names.extend((username, is_login_success, is_suspend))

        ops = {
            'key_value_types': key_value_types,
            'detail_names': detail_names,
            'trigger_type': mechanic.get('event_name')
        }

        context.update(ops)
        self.logger.info('========== Finished showing Add Action page ==========')
        return context

    def post(self, request, *args, **kwargs):
        context = super(AddAction, self).get_context_data(**kwargs)
        campaign_id = context['campaign_id']
        mechanic_id = context['mechanic_id']

        kv_type_map = {
            "Numeric": "numeric", "Freetext": "text", "Timestamp": "timestamp"
        }

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
                if data_type == 'from_event':
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

        elif reward_type == 'response':
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
                "action_type_id": 3,
                "data": []
            }
            counter = request.POST.get('data_counter') or 1
            for i in range(int(counter)):
                suffix = '' if i == 0 else str(i + 1)
                reward_data_type = 'reward_data_type' + suffix
                data_type = request.POST.get(reward_data_type)
                if not data_type:
                    continue
                if data_type == 'from_event':
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

        success, data, message = self.create_reward(campaign_id, mechanic_id, params)

        if not success:
            return JsonResponse({"status": 3, "msg": message})

        action_id = data.get("id", '')
        # add limitation
        limit_to = request.POST.get('limit_to')
        if limit_to:
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
            if not success:
                return JsonResponse({"status": 3, "msg": message})
        messages.success(request, 'Save successfully')
        return JsonResponse({"status": 2, "msg": message})

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
        link_bank = {'term': 'created_sof', 'description': 'Create SOF'}
        created_order = {'term': 'create_order', 'description': 'Create Order'}
        limit_reached = {'term': 'limit_reached', 'description': 'Limit Reached'}
        filtered.extend([link_bank, created_order, limit_reached])
        return filtered

    def get_mechanic(self, campaign_id, mechanic_id):
        url = api_settings.GET_MECHANIC_DETAIL.format(bak_rule_id=campaign_id, mechanic_id=mechanic_id)
        success, status_code, status_message, data = RestfulHelper.send("GET", url, {}, self.request, "getting mechanic detail")
        return success, data
