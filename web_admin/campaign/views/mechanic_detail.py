from django.views.generic.base import TemplateView
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

    def dispatch(self, request, *args, **kwargs):
        self.logger = build_logger(request, __name__)
        return super(MechanicDetail, self).dispatch(request, *args, **kwargs)


    def get(self, request, *args, **kwargs):
        context = super(MechanicDetail, self).get_context_data(**kwargs)
        campaign_id = kwargs['campaign_id']
        mechanic_id = kwargs['mechanic_id']
        success, data = self.get_mechanic(campaign_id, mechanic_id)
        if not success:
            return render(request, self.template_name, context)

        success, cons = self.get_condition_list(campaign_id, mechanic_id)
        if not success:
            return render(request, self.template_name, context)

        data['condition_list'] = cons
        for condition in cons:
            success, coms = self.get_comparison_list(campaign_id, mechanic_id, condition['id'])
            if not success:
                continue
            condition['comparison_list'] = coms
            success, filter = self.get_condition_filter(campaign_id, mechanic_id, condition['id'])
            if not success:
                continue
            condition['filter'] = filter

        data['action_list'] = self.build_action_list(campaign_id, mechanic_id)

        # Get result for Count Of
        for con in data.get('condition_list'):
            if con.get('filter_type') != 'count_of':
                continue
            if not con.get('filter'):
                continue
            for filter in con['filter'][::]:
                if filter.get('key_name') == 'event_name':
                    con['count_key_name'] = filter.get('key_value')
                    con['filter'].remove(filter)
                elif filter.get('key_name') == 'event_created_timestamp':
                    if '@@@@event_created_timestamp@@-minutes(' in filter.get('key_value'):
                        con['within'] = 'Timebox'
                        con['timebox'] = filter['key_value'].split('@@@@event_created_timestamp@@-minutes(')[1].split(')@@')[0]
                    elif '@@event_created_timestamp@@' not in filter.get('key_value'):
                        con['within'] = 'Date'
                        if filter.get('operator') == '>=':
                            con['within_start'] = filter.get('key_value')
                        if filter.get('operator') == '<=':
                            con['within_end'] = filter.get('key_value')
                    con['filter'].remove(filter)

        context.update({
            'mechanic': data,
        })

        return render(request, self.template_name, context)

    def build_action_list(self, campaign_id, mechanic_id):
        ret = []
        success, action_list = self.get_rewards_list(campaign_id, mechanic_id)

        for action in action_list:
            if action['is_deleted']:
                continue

            action_data = action['action_data']
            action_type_id = action['action_type']['id']

            if action_type_id == 1:
                reward_to = self.get_action_data_value(action_data, 'payee_user.user_id')
                reward_to = self.get_person_name(reward_to)
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
                reward_to = self.get_person_name(reward_to)
                action['reward_to'] = reward_to
                action['recipient'] = self.get_action_data_value(action_data, 'user_type').title()

            success, limitation_list = self.get_limitation_list(campaign_id, mechanic_id, action['id'])

            action['limitation_list'] = []
            for limitation in limitation_list:
                if limitation['is_deleted']:
                    continue

                limitation_data = limitation['filters']
                reward_to = self.get_limitation_data_value(limitation_data, 'user_id')
                reward_to = self.get_person_name(reward_to)
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

    def get_person_name(self, key):
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