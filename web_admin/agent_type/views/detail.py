import logging

from django.conf import settings
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods

logger = logging.getLogger(__name__)


class DetailView(TemplateView, RESTfulMethods):
    template_name = "agent_type/agent_type_detail.html"

    def get_context_data(self, **kwargs):
        try:
            context = super(DetailView, self).get_context_data(**kwargs)
            agent_type_id = context['agentTypeId']

            return self._get_agent_type_detail(agent_type_id)



        except:
            context = {'agent_type_info': {}}
            return context

    def _get_agent_type_detail(self, agent_type_id):
        data, success = self._get_method(api_path=settings.AGENT_TYPE_DETAIL_URL.format(agent_type_id),
                                         func_description="Agent Type Detail",
                                         logger=logger)
        context = {'agent_type_info': data,
                   'msg': self.request.session.pop('agent_type_update_msg', None)}
        return context