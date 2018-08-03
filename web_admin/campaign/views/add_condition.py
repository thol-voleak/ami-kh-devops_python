from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from campaign.utils import get_profile_details_event_list
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
from services.views.tier_levels.utils import get_label_levels

import logging

from web_admin.utils import build_logger

logger = logging.getLogger(__name__)


class AddCondition(TemplateView, GetHeaderMixin):
    template_name = "campaign/add_condition.html"
    logger = logger

    def __init__(self):
        self._operator_map = {
            "Less Than": '<', "More Than": '>', "Equal to": '=',
            "Not Equal to": '!=', "Less than or Equal to": '<=',
            "More than or Equal to": '>=',
            "Contains": "contains",
            "Is Part of": "in_list",
            "Is Not Part of": "not_in_list",
            "Is blank": "is_blank",
            "Is not blank": "is_not_blank",
        }

        self._kv_type_map = {
            "Numeric": "numeric",
            "Freetext": "text",
            "Timestamp": "timestamp"
        }
        super(AddCondition, self).__init__()

    def dispatch(self, request, *args, **kwargs):
        self.logger = build_logger(self.request, __name__)
        return super(AddCondition, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start showing Add Condition page ==========')
        context = super(AddCondition, self).get_context_data(**kwargs)
        context['dtp_start_date'] = datetime.now().strftime("%Y-%m-%d")
        context['dtp_end_date'] = datetime.now().strftime("%Y-%m-%d")
        operations = ["Equal to", "Not Equal to", "Less Than", "More Than", "Is blank", "Is not blank",
                      "Less than or Equal to", "More than or Equal to"]
        freetext_ops = ["Equal to", "Not Equal to", "Is blank", "Is not blank", "Contains"]
        freetext_ops_2 = ["Equal to", "Not Equal to", "Is Part of", "Is Not Part of", "Is blank", "Is not blank", "Contains"]
        numeric_ops = ["Equal to", "Not Equal to", "Is Part of", "Is Not Part of", "Less Than", "More Than", "Is blank", "Is not blank",
                       "Less than or Equal to", "More than or Equal to"]
        key_value_types = ["Numeric", "Freetext", "Timestamp"]
        filter_key_value_types = ["Numeric", "Timestamp"]
        sum_of_operators = ["Equal to", "Not Equal to", "Less than or Equal to", "More than or Equal to"]
        count_of_operators = ["Equal to", "Less Than", "More Than", "More than or Equal to", "Less than or Equal to"]
        count_consecutive_of_operators = ["Equal to", "More than or Equal to"]
        profile_details_freetext_ops = ["Equal to", "Not Equal to", "Is Part of", "Is blank", "Is not blank", "Contains"]
        profile_details_numeric_ops = ["Equal to", "Not Equal to", "Is Part of", "Less Than", "More Than", "Is blank", "Is not blank",
                                       "Less than or Equal to", "More than or Equal to"]
        # sum_key_name = [{
        #         'value': 'amount',
        #         'text': 'Amount'
        #     }, {
        #         'value': 'fee',
        #         'text': 'Fee'
        #     },{
        #         'value': 'bonus',
        #         'text': 'Bonus'
        #     },{
        #         'value': 'settlement_amount',
        #         'text': 'Settlement Amount'
        #     }]
        sum_key_name = self.get_label_name()
        all_terms = list(terms_mapping.objects.all())
        detail_names = self._filter_detail_names(all_terms)
        username = {'term': 'username', 'description': ''}
        is_login_success = {'term': 'is_login_success', 'description': ''}
        is_suspend = {'term': 'is_suspend', 'description': ''}
        referrer_user_id_term = {'term': 'referrer_user_id', 'description': ''}
        referrer_user_type_term = {'term': 'referrer_user_type', 'description': ''}
        detail_names.extend((username, is_login_success, is_suspend))
        detail_names.extend((referrer_user_id_term, referrer_user_type_term))
        detail_names.extend(sum_key_name)
        trigger = self._filter_trigger(all_terms)

        campaign_id = context['campaign_id']
        mechanic_id = context['mechanic_id']
        success, mechanic = self.get_mechanic(campaign_id, mechanic_id)

        ops = {
            'operations': operations,
            'numeric_ops': numeric_ops,
            'key_value_types': key_value_types,
            'detail_names': detail_names,
            'profile_detail_names': get_profile_details_event_list(),
            'trigger': trigger,
            'freetext_ops': freetext_ops,
            'freetext_ops_2': freetext_ops_2,
            'profile_details_freetext_ops': profile_details_freetext_ops,
            'profile_details_numeric_ops': profile_details_numeric_ops,
            'filter_key_value_types': filter_key_value_types,
            'sum_of_operators': sum_of_operators,
            'count_of_operators': count_of_operators,
            'count_consecutive_of_operators': count_consecutive_of_operators,
            'sum_key_name': sum_key_name,
            'trigger_type': mechanic.get('event_name')
        }

        context.update(ops)
        self.logger.info('========== Finished showing Add Condition page ==========')
        return context

    def post(self, request, *args, **kwargs):
        context = super(AddCondition, self).get_context_data(**kwargs)
        campaign_id = context['campaign_id']
        mechanic_id = context['mechanic_id']

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
                operator_name = 'operator_' + suffix
                key_value_name = 'key_value_' + suffix

                if not request.POST.get(key_value_name) and not self._is_blank_operator(request, operator_name):
                    continue

                params = self._build_create_filter_params(request, detail_name, key_value_type, operator_name, key_value_name)
                success, data, message = self.create_comparison(campaign_id, mechanic_id, condition_id, params)
                if not success:
                    return JsonResponse({"status": 3, "msg": message})

            elif condition_type == 'profile_details':
                params = {'filter_type': condition_type}
                profile_detail_actor = request.POST.get('actor_' + suffix)
                if profile_detail_actor:
                    params['profile_detail_actor'] = profile_detail_actor

                success, data, message = self.create_condition(campaign_id, mechanic_id, params)
                if not success:
                    return JsonResponse({"status": 3, "msg": message})

                condition_id = data['id']
                key_value_type = 'key_value_type_' + suffix
                detail_name = 'detail_name_' + suffix
                operator_name = 'operator_' + suffix
                key_value_name = 'key_value_' + suffix

                if not request.POST.get(key_value_name) and not self._is_blank_operator(request, operator_name):
                    continue

                params = self._build_create_filter_params(request, detail_name, key_value_type, operator_name, key_value_name)
                success, data, message = self.create_comparison(campaign_id, mechanic_id, condition_id, params)
                if not success:
                    return JsonResponse({"status": 3, "msg": message})

            elif condition_type == 'sum_of':
                params = {'filter_type': condition_type, 'sum_key_name': sum_key_name}
                success, data, message = self.create_condition(campaign_id, mechanic_id, params)
                if not success:
                    return JsonResponse({"status": 3, "msg": message})

                condition_id = data['id']

                params = {
                    'key_name': 'sum_result',
                    'key_value_type': 'numeric',
                    'operator': self._operator_map[sum_operator],
                    'key_value': sum_key_value,
                }
                success, data, message = self.create_comparison(campaign_id, mechanic_id, condition_id, params)
                if not success:
                    return JsonResponse({"status": 3, "msg": message})

                for i in range(1, int(filter_counter) + 1):
                    prefix = str(i)
                    key_value_type = prefix + '_key_value_type_' + suffix
                    detail_name = prefix + '_detail_name_' + suffix
                    operator_name = prefix + '_operator_' + suffix
                    key_value_name = prefix + '_key_value_' + suffix

                    if not request.POST.get(key_value_name) and not self._is_blank_operator(request, operator_name):
                        continue
                    params = self._build_create_filter_params(request, detail_name, key_value_type, operator_name, key_value_name)
                    success, data, message = self.create_filter(campaign_id, mechanic_id, condition_id, params)
                    if not success:
                        return JsonResponse({"status": 3, "msg": message})
            elif condition_type == 'count_of':
                count_count_of = request.POST.get('count_' + suffix)
                count_of_operator = request.POST.get('count_of_operator_' + suffix)
                count_of_filter_counter = request.POST.get('filter_count_of_count_' + suffix) or 0
                within_type = request.POST.get('within_' + suffix)
                event_name_filter_counter = request.POST.get('event_name_' + suffix)
                success, condition_id, message = self.create_common_count_of_condition(request, suffix, campaign_id, mechanic_id, condition_type,
                                                                                       count_of_operator, count_count_of, within_type,
                                                                                       event_name_filter_counter, count_of_filter_counter)
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
                success, condition_id, message = self.create_common_count_of_condition(request, suffix, campaign_id, mechanic_id, condition_type,
                                                                                       count_of_operator, count_count_of, within_type,
                                                                                       event_name_filter_counter, count_of_filter_counter)
                if not success:
                    return JsonResponse({"status": 3, "msg": message})
                # consecutive key detail
                condition_reset_event = request.POST.get('condition_reset_event_' + suffix)
                params = self._build_create_filter_params(request, 'consecutive_detail_name_' + suffix, 'consecutive_key_value_type_' + suffix,
                                                          'consecutive_operator_' + suffix, 'consecutive_key_value_' + suffix)
                params["is_consecutive_key"] = True
                success, data, message = self.create_filter(campaign_id, mechanic_id, condition_id, params)
                if not success:
                    return JsonResponse({"status": 3, "msg": message})

                # condition reset value
                params = {
                    'key_name': 'event_name',
                    'key_value_type': 'text',
                    'operator': '=',
                    'key_value': condition_reset_event,
                }
                success, data, message = self.create_reset_filter(campaign_id, mechanic_id, condition_id, params)
                if not success:
                    return JsonResponse({"status": 3, "msg": message})

                for i in range(1, int(count_of_reset_filter_counter) + 1):
                    prefix = str(i)
                    key_value_type = prefix + '_reset_filter_key_value_type_' + suffix
                    detail_name = prefix + '_reset_filter_detail_name_' + suffix
                    operator_name = prefix + '_reset_filter_operator_' + suffix
                    key_value_name = prefix + '_reset_filter_key_value_' + suffix

                    if not request.POST.get(key_value_name) and not self._is_blank_operator(request, operator_name):
                        continue
                    params = self._build_create_filter_params(request, detail_name, key_value_type, operator_name, key_value_name)
                    success, data, message = self.create_reset_filter(campaign_id, mechanic_id, condition_id, params)
                    if not success:
                        return JsonResponse({"status": 3, "msg": message})

        messages.success(request, 'Save successfully')
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

    def create_common_count_of_condition(self, request, suffix, campaign_id, mechanic_id, condition_type, count_of_operator, count_count_of,
                                         within_type, event_name_filter_counter, count_of_filter_counter):
        params = {'filter_type': condition_type}
        success, data, message = self.create_condition(campaign_id, mechanic_id, params)
        if not success:
            return success, None, message

        condition_id = data['id']

        params = {
            'key_name': 'count_result',
            'key_value_type': 'numeric',
            'operator': self._operator_map[count_of_operator],
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
            operator_name = prefix + '_operator_' + suffix
            key_value_name = prefix + '_key_value_' + suffix

            if not request.POST.get(key_value_name) and not self._is_blank_operator(request, operator_name):
                continue
            params = self._build_create_filter_params(request, detail_name, key_value_type, operator_name, key_value_name)
            success, data, message = self.create_filter(campaign_id, mechanic_id, condition_id, params)
            if not success:
                return success, None, message
        success = True
        return success, condition_id, message

    def _is_blank_operator(self, request, operator_name):
        operator = self._operator_map[request.POST.get(operator_name)]
        return operator == "is_blank" or operator == "is_not_blank"

    def _build_create_filter_params(self, request, detail_name, kv_type_name, operator_name, key_value_name):
        key_name = request.POST.get(detail_name)
        kv_type = self._kv_type_map[request.POST.get(kv_type_name)]
        operator = self._operator_map[request.POST.get(operator_name)]
        key_value = request.POST.get(key_value_name)
        params = {
            "key_name": key_name,
            "key_value_type": kv_type,
            "operator": operator,
        }
        if not self._is_blank_operator(request, operator_name):
            params["key_value"] = key_value
        return params

    def get_label_name(self):
        label_levels = self.request.session.get('tier_levels')
        if not label_levels:
            label_levels = get_label_levels(self.request)
        extend = []
        for lvl in label_levels:
            tier_level_name = lvl.get('name')
            if lvl.get('label'):
                extend.append({'term': str(tier_level_name).lower(), 'description': tier_level_name + ": " + lvl.get('label')})
            else:
                extend.append({'term': str(tier_level_name).lower(), 'description': tier_level_name + ": [No Label Set]"})
        return extend
