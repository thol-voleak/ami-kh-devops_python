from web_admin.restful_methods import RESTfulMethods
from web_admin import api_settings, setup_logger

import logging

logger = logging.getLogger(__name__)


class AgentAPIService(RESTfulMethods):
    def get_agent_profile(self, agent_id):
        data, success = self._get_method(api_path=api_settings.AGENT_DETAIL_PATH.format(agent_id=agent_id),
                                         func_description="Agent Profile",
                                         logger=logger)
        return data

    def get_agent_types(self):
        data, success = self._get_method(api_path=api_settings.GET_AGENT_TYPES_PATH,
                                         func_description="Agent Type List",
                                         logger=logger,
                                         is_getting_list=True)
        return data, success

    def get_agent_detail(self, agent_id):
        data, success = self._get_method(api_path=api_settings.AGENT_DETAIL_PATH.format(agent_id=agent_id),
                                         func_description="Agent detail",
                                         logger=logger)
        context = {
            'agent': data,
            'agent_id': agent_id,
            'msg': self.request.session.pop('agent_registration_msg', None)
        }
        return context, success

    def get_agent_identity(self, agent_id):
        data, success = self._get_method(api_path=self.get_agent_identity_url.format(agent_id=agent_id),
                                         func_description="Get agent identity",
                                         logger=logger)
        context = {
            'agent_identities': data
        }
        return context, success

    def get_currencies(self, agent_id):
        data, success = self._get_method(api_path=api_settings.GET_AGET_BALANCE.format(agent_id),
                                         func_description="Agent Currencies",
                                         logger=logger,
                                         is_getting_list=True)
        currencies_str = ''
        if success:
            currencies_str = ', '.join([elem["currency"] for elem in data])

        return currencies_str, success

    def get_agent_type_name(self, agent_type_id):
        agent_types_list, success = self._get_method(api_path=api_settings.AGENT_TYPES_LIST_URL,
                                                     func_description="Agent types list from backend",
                                                     logger=logger,
                                                     is_getting_list=True)
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
