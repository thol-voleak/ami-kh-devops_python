from web_admin.api_settings import AGENT_TYPE_DETAIL_URL
from web_admin.restful_methods import RESTfulMethods

from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class DetailView(TemplateView, RESTfulMethods):
    template_name = "agent_type/agent_type_detail.html"

    def get_context_data(self, **kwargs):
        try:
            logger.info('========== Start get agent type detail ==========')
            context = super(DetailView, self).get_context_data(**kwargs)

            agent_type_id = context['agentTypeId']
            data, success = self._get_method(api_path=AGENT_TYPE_DETAIL_URL.format(agent_type_id),
                                             func_description="Agent Type Detail",
                                             logger=logger)
            context = {
                'agent_type_info': data,
                'msg': self.request.session.pop('agent_type_update_msg', None)
            }

            logger.info('========== End get agent type detail ==========')
            return context
        except Exception as e:
            logger.error(e)
            context = {'agent_type_info': {}}
            return context
