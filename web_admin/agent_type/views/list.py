import logging

from django.conf import settings
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods

logger = logging.getLogger(__name__)


class ListView(TemplateView, RESTfulMethods):
    template_name = "agent_type/agent_types_list.html"

    def get_context_data(self, **kwargs):
        data = self.get_agent_types_list()
        result = {'data': data,
                  'msg': self.request.session.pop('agent_type_create_msg', None),
                  'del_msg': self.request.session.pop('agent_type_delete_msg', None)}

        return result

    def get_agent_types_list(self):
        data, success = self._get_method(api_path=settings.AGENT_TYPES_LIST_URL,
                                         func_description="Agent Type List",
                                         logger=logger,
                                         is_getting_list=True)
        return data