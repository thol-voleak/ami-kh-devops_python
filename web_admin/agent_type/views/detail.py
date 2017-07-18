from authentications.utils import get_correlation_id_from_username
from web_admin.api_settings import AGENT_TYPE_DETAIL_URL
from web_admin.restful_methods import RESTfulMethods
from web_admin import setup_logger

from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class DetailView(TemplateView, RESTfulMethods):
    template_name = "agent_type/agent_type_detail.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start showing Agent Type Detail page ==========')
        try:
            context = super(DetailView, self).get_context_data(**kwargs)

            agent_type_id = context['agentTypeId']
            data, success = self._get_method(api_path=AGENT_TYPE_DETAIL_URL.format(agent_type_id),
                                             func_description="Agent Type Detail",
                                             logger=logger)
            context = {
                'agent_type_info': data,
                'msg': self.request.session.pop('agent_type_update_msg', None)
            }

            self.logger.info('========== Finished showing Agent Type Detail page ==========')
            return context
        except Exception as e:
            self.logger.error(e)
            context = {'agent_type_info': {}}
            self.logger.info('========== Finished showing Agent Type Detail page ==========')
            return context
