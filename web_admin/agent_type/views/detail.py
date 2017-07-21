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
        context = super(DetailView, self).get_context_data(**kwargs)
        agent_type_id = context['agentTypeId']
        params = {"id": agent_type_id}
        data, success = self._post_method(AGENT_TYPE_DETAIL_URL, func_description="", logger=logger, params=params, only_return_data=True)
        if success:
            context = {
                'agent_type_info': data[0],
                'msg': self.request.session.pop('agent_type_update_msg', None)
            }
        else:
            context = {
                'agent_type_info': {},
                'msg': self.request.session.pop('agent_type_update_msg', None)
            }

        self.logger.info('========== Finished showing Agent Type Detail page ==========')
        return context
