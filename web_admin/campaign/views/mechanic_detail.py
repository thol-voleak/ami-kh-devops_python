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

        success, action = self.get_rewards_list(campaign_id, mechanic_id)
        if not success:
            return render(request, self.template_name, context)

        data['reward'] = {}
        if len(action) > 0:
            reward = {}
            action = action[0]
            action_id = action['id']
            reward['reward_type'] = action['action_type']['name']
            reward['id'] = action['action_type']['id']
            if action['action_type']['id'] == 1:
                for j in action['action_data']:
                    if j['key_name'] == 'payee_user.user_id':
                        if j['key_value'] in self.person.keys():
                            reward['reward_to'] = self.person[j['key_value']]
                    if j['key_name'] == 'payee_user.user_type':
                        reward['recipient'] = j['key_value']
                    if j['key_name'] == 'amount':
                        reward['amount'] = j['key_value']
            elif action['action_type']['id'] == 2:
                reward['reward_type'] = 'Send Notification'
                reward['reward_to'] = action['user_id']
                reward['recipient'] = action['user_type']
                for action_data in action['action_data']:
                    if action_data['key_name'] == 'notification_url':
                        reward['send_to'] = action_data['key_value']
                reward['data_to_be_sent'] = action['action_data']
            elif action['action_type']['id'] == 4:
                reward['reward_type'] = 'Suspend Account'
                for j in action['action_data']:
                    if j['key_name'] == 'user_id':
                        if j['key_value'] in self.person.keys():
                            reward['reward_to'] = self.person[j['key_value']]
                    if j['key_name'] == 'user_type':
                        if j['key_value'] == 'customer':
                            reward['recipient'] = 'Customer'
                        elif j['key_value'] == 'agent':
                            reward['recipient'] = 'Agent'
                        else:
                            reward['recipient'] = j['key_value']
            data['reward'] = reward

            success, limitation = self.get_limitation_list(campaign_id, mechanic_id, action_id)
            if not success:
                return render(request, self.template_name, context)

            data['limitation_list'] = []
            for l in limitation:
                if l['is_deleted']:
                    continue
                for filter_limit in l['filters']:
                    if filter_limit['key_name'] == 'user_id':
                        if filter_limit['key_value'] in self.person.keys():
                            l['reward_to'] = self.person[filter_limit['key_value']]
                    if filter_limit['key_name'] == 'user_type':
                        l['recipient'] = filter_limit['key_value']
                data['limitation_list'].append(limitation)

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