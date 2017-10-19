from web_admin.restful_methods import RESTfulMethods
from web_admin import api_settings, setup_logger

import logging

logger = logging.getLogger(__name__)


class AgentAPIService(RESTfulMethods):
    def get_agent_profile(self, agent_id):
        body = {'id': agent_id}
        data, success = self._post_method(api_path=api_settings.AGENT_DETAIL_PATH,
                                          func_description="Agent detail",
                                          logger=logger, params=body)
        data = data.get('agents', [])
        return data[0]

    def get_agent_types(self, agent_id):
        # body = {'id': agent_id}
        data, success = self._post_method(api_path=api_settings.GET_AGENT_TYPES_PATH,
                                         func_description="Agent Type List",
                                         logger=logger)
        return data, success

    def get_agent_detail(self, agent_id):
        body = {'id': agent_id}
        data, success = self._post_method(api_path=api_settings.AGENT_DETAIL_PATH,
                                          func_description="Agent detail",
                                          logger=logger, params=body)
        data = data.get('agents', [])
        context = {
            'agent': data[0],
            'agent_id': agent_id,
            'msg': self.request.session.pop('agent_registration_msg', None)
        }
        return context, success

    def get_agent_identity(self, agent_id):
        body = {'agent_id': agent_id}
        data, success = self._post_method(api_path=api_settings.GET_AGENT_IDENTITY_URL.format(agent_id=agent_id),
                                         func_description="Get agent identity",
                                         logger=logger,
                                         params=body)
        context = {
            'agent_identities': data
        }
        return context, success

    def get_currencies(self, agent_id):
        url = api_settings.GET_REPORT_AGENT_BALANCE
        body = {
                'user_id': agent_id,
                'user_type': 2}
        data, success = self._post_method(api_path=url,
                                          func_description="currency list by agent",
                                          logger=logger,
                                          params=body)
        currencies_str = ''
        if success and len(data) > 0:
            currencies_str = ', '.join([elem["currency"] for elem in data])

        return currencies_str, success

    def get_agent_type_name(self, agent_type_id):
        agent_types_list, success = self._post_method(api_path=api_settings.AGENT_TYPES_LIST_URL,
                                          func_description="Agent Type List",
                                          logger=logger)
        if success:
            my_id = int(agent_type_id)
            for x in agent_types_list:
                if x['id'] == my_id:
                    agent_type_name = x['name']
                    return agent_type_name, True
            data = 'Unknown', True
        else:
            data = None, False
        return data
