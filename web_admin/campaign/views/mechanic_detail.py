from django.views.generic.base import TemplateView

from campaign.utils import get_profile_details_event_list
from web_admin.get_header_mixins import GetHeaderMixin
from django.shortcuts import render
from web_admin.utils import build_logger
import logging
from web_admin import api_settings
from web_admin.restful_helper import RestfulHelper


class MechanicDetail(TemplateView, GetHeaderMixin):

    template_name = "campaign/mechanic_detail.html"
    logger = logging.getLogger(__name__)
    person = {
        '@@user_id@@':'Actor who registered',
        '@@payer_user_id@@':'Actor that paid for the transaction',
        '@@payee_user_id@@':'Actor that received the transaction',
        '@@initiator_user_id@@':'Actor that created the transaction'
    }

    person_1 = {
        '@@user_id@@': 'Actor whose profile is updated'
    }

    def dispatch(self, request, *args, **kwargs):
        self.logger = build_logger(request, __name__)
        return super(MechanicDetail, self).dispatch(request, *args, **kwargs)


    def get(self, request, *args, **kwargs):
        context = super(MechanicDetail, self).get_context_data(**kwargs)
        campaign_id = kwargs['campaign_id']
        mechanic_id = kwargs['mechanic_id']

        rule = self.get_rule_detail(campaign_id)
        context.update({
            'rule': rule,
        })

        success, data = self.get_mechanic(campaign_id, mechanic_id)
        if not success:
            return render(request, self.template_name, context)
        event_name = data['event_name']

        success, cons = self.get_condition_list(campaign_id, mechanic_id)
        if not success:
            return render(request, self.template_name, context)
        cons = [x for x in cons if not x['is_deleted']]

        data['condition_list'] = cons
        for condition in cons:
            success, coms = self.get_comparison_list(campaign_id, mechanic_id, condition['id'])
            condition['comparison_list'] = coms

            success, list_filter = self.get_condition_filter(campaign_id, mechanic_id, condition['id'])
            list_filter = [x for x in list_filter if not x['is_deleted']]

            if condition.get('filter_type') == 'count_consecutive_of':
                success, list_reset_filter = self.get_condition_reset_filters(campaign_id, mechanic_id, condition['id'])
                self.build_consecutive_data(condition, list_filter, list_reset_filter)

            condition['filter'] = list_filter

        data['action_list'] = self.build_action_list(campaign_id, mechanic_id, event_name)

        # Get result for Count Of
        for con in data.get('condition_list'):
            # set flag to get only first event_name (in case there are multiple event_names)
            flag = 0
            if con.get('filter_type') != 'count_of':
                continue
            if not con.get('filter'):
                continue
            for filter in con['filter'][::]:
                if flag == 0 and filter.get('key_name') == 'event_name':
                    con['count_key_name'] = filter.get('key_value')
                    con['filter'].remove(filter)
                    flag = 1
                elif filter.get('key_name') == 'event_created_timestamp':
                    self.build_within_from_filter(con, filter)
                    con['filter'].remove(filter)

        context.update({
            'mechanic': data,
            'profile_detail_names': get_profile_details_event_list(),
        })

        return render(request, self.template_name, context)

    def build_consecutive_data(self, condition, list_filter, list_reset_filter):
        filter_event_name = self.pop_filter_by_key_name(list_filter, "event_name")
        condition["filter_event_name"] = filter_event_name

        filter_event_created_timestamp = self.pop_filter_by_key_name(list_filter, "event_created_timestamp")
        self.build_within_from_filter(condition, filter_event_created_timestamp)

        filter_event_created_timestamp = self.pop_filter_by_key_name(list_filter, "event_created_timestamp")
        self.build_within_from_filter(condition, filter_event_created_timestamp)

        filter_consecutive = self.pop_filter_if_is_consecutive(list_filter)
        condition["filter_consecutive"] = filter_consecutive

        reset_filter_event_name = self.pop_filter_by_key_name(list_reset_filter, "event_name")
        condition["reset_filter_event_name"] = reset_filter_event_name

        condition["list_reset_filter"] = list_reset_filter

    def build_within_from_filter(self, condition, filter):
        if not filter:
            return

        if 'minutes' in filter.get('key_value'):
            condition['within'] = 'Timebox'
            condition['timebox'] = filter['key_value'].split('@@@@event_created_timestamp@@-minutes(')[1].split(')@@')[0]
        elif '@@event_created_timestamp@@' not in filter.get('key_value'):
            condition['within'] = 'Date'
            if filter.get('operator') == '>=':
                condition['within_start'] = filter.get('key_value')
            if filter.get('operator') == '<=':
                condition['within_end'] = filter.get('key_value')

    def pop_filter_by_key_name(self, filter_list, key_name):
        for filter in filter_list:
            if filter['key_name'] == key_name:
                filter_list.remove(filter)
                return filter
        return None

    def pop_filter_if_is_consecutive(self, filter_list):
        for filter in filter_list:
            if filter.get('is_consecutive_key'):
                filter_list.remove(filter)
                return filter
        return None

    def build_action_list(self, campaign_id, mechanic_id, event_name):
        ret = []
        success, action_list = self.get_rewards_list(campaign_id, mechanic_id)

        for action in action_list:
            if action['is_deleted']:
                continue

            action_data = action['action_data']
            action_type_id = action['action_type']['id']

            if action_type_id == 1:
                reward_to = self.get_action_data_value(action_data, 'payee_user.user_id')
                reward_to = self.get_person_name(reward_to, event_name)
                action['reward_to'] = reward_to
                action['recipient'] = self.get_action_data_value(action_data, 'payee_user.user_type')
                action['amount'] = self.get_action_data_value(action_data, 'amount')
                action['product_service_id'] = self.get_action_data_value(action_data, 'product_service_id')
                action['payer_id'] = self.get_action_data_value(action_data, 'payer_user.user_id')
                action['payer_sof_id'] = self.get_action_data_value(action_data, 'payer_user.sof.id')
            elif action_type_id == 2:
                action['reward_to'] = action['user_id']
                action['recipient'] = action['user_type']
                action['send_to'] = self.get_action_data_value(action_data, 'notification_url')
            elif action_type_id == 4:
                reward_to = self.get_action_data_value(action_data, 'user_id')
                reward_to = self.get_person_name(reward_to, event_name)
                action['reward_to'] = reward_to
                action['recipient'] = self.get_action_data_value(action_data, 'user_type').title()
            elif action_type_id == 5:
                action['voucher_group'] = self.get_action_data_value(action_data, 'voucher_group')
                action['expiration_date'] = self.get_action_data_value(action_data, 'expiration_date')
                reward_to = self.get_action_data_value(action_data, 'user_id')
                reward_to = self.get_person_name(reward_to, event_name)
                action['reward_to'] = reward_to
                action['recipient'] = self.get_action_data_value(action_data, 'user_type').title()

            success, limitation_list = self.get_limitation_list(campaign_id, mechanic_id, action['id'])

            action['limitation_list'] = []
            for limitation in limitation_list:
                if limitation['is_deleted']:
                    continue

                limitation_data = limitation['filters']
                reward_to = self.get_limitation_data_value(limitation_data, 'user_id')
                reward_to = self.get_person_name(reward_to, event_name)
                limitation['reward_to'] = reward_to
                limitation['recipient'] = self.get_limitation_data_value(limitation_data, 'user_type')
                action['limitation_list'].append(limitation)
            ret.append(action)
        return ret

    def get_limitation_data_value(self, limitation_data, key_name):
        for data in limitation_data:
            if data['key_name'] == key_name:
                return data['key_value']
        return None

    def get_action_data_value(self, action_data, key_name):
        for data in action_data:
            if data['key_name'] == key_name:
                return data['key_value']
        return None

    def get_person_name(self, key, event_name):
        if event_name == 'update_profile':
            if key in self.person_1.keys():
                return self.person_1[key]
        else:
            if key in self.person.keys():
                return self.person[key]

        return None

    def get_mechanic(self, campaign_id, mechanic_id):
        url = api_settings.GET_MECHANIC_DETAIL.format(bak_rule_id=campaign_id, mechanic_id=mechanic_id)
        success, status_code, status_message, data = RestfulHelper.send("GET", url, {}, self.request, "getting mechanic detail")
        return success, data

    def get_condition_list(self, campaign_id, mechanic_id):
        url = api_settings.GET_CONDITION_LIST.format(bak_rule_id=campaign_id, bak_mechanic_id=mechanic_id)
        success, status_code, status_message, data = RestfulHelper.send("GET", url, {}, self.request, "getting condition list", "data")
        return success, data

    def get_comparison_list(self, campaign_id, mechanic_id, condition_id):
        url = api_settings.GET_COMPARISON_LIST.format(bak_rule_id=campaign_id, bak_mechanic_id=mechanic_id, bak_condition_id=condition_id)
        success, status_code, status_message, data = RestfulHelper.send("GET", url, {}, self.request, "getting comparison list", "data")
        return success, data

    def get_rewards_list(self, campaign_id, mechanic_id):
        url = api_settings.GET_REWARD_LIST.format(bak_rule_id=campaign_id, bak_mechanic_id=mechanic_id)
        success, status_code, status_message, data = RestfulHelper.send("GET", url, {}, self.request, "getting reward list", "data")
        return success, data


    def get_limitation_list(self, campaign_id, mechanic_id, action_id):
        url = api_settings.GET_LIMITION_LIST.format(bak_rule_id=campaign_id, bak_mechanic_id=mechanic_id, bak_action_id=action_id)
        success, status_code, status_message, data = RestfulHelper.send("GET", url, {}, self.request, "getting limitation list", "data")
        return success, data

    def get_condition_filter(self, campaign_id, mechanic_id, condition_id):
        url = api_settings.GET_CONDITION_FILTER.format(rule_id=campaign_id, mechanic_id=mechanic_id, condition_id=condition_id)
        success, status_code, status_message, data = RestfulHelper.send("GET", url, {}, self.request, "getting condition filter", "data")
        return success, data

    def get_rule_detail(self, campaign_id):
        url = api_settings.GET_CAMPAIGNS_DETAIL.format(bak_rule_id=campaign_id)
        success, status_code, status_message, data = RestfulHelper.send("GET", url, {}, self.request, "getting rule detail", "data")
        return data

    def get_condition_reset_filters(self, campaign_id, mechanic_id, condition_id):
        url = api_settings.GET_CONDITION_RESET_FILTERS.format(rule_id=campaign_id, mechanic_id=mechanic_id, condition_id=condition_id)
        success, status_code, status_message, data = RestfulHelper.send("GET", url, {}, self.request, "getting condition reset filter", "data")
        return success, data