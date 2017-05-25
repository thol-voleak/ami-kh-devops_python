from web_admin.api_settings import AGENT_TYPES_LIST_URL
from web_admin.restful_methods import RESTfulMethods

from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class ListView(TemplateView, RESTfulMethods):
    template_name = "agent_type/agent_types_list.html"

    def get_context_data(self, **kwargs):
        logger.info('========== Start showing Agent Type List page ==========')
        data = self.get_agent_types_list()
        result = {
            'data': data,
            'del_msg': self.request.session.pop('agent_type_delete_msg', None)
        }
        logger.info('========== Finished showing Agent Type List page ==========')
        return result

    def get_agent_types_list(self):
        data, success = self._get_method(api_path=AGENT_TYPES_LIST_URL,
                                         func_description="Agent Type List",
                                         logger=logger,
                                         is_getting_list=True)
        return data
