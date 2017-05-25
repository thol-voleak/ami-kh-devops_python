import logging

from django.conf import settings
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods

logger = logging.getLogger(__name__)

'''
Author: Steve Le
History:
# 2017-05-23
- Init
- API 1: DELETE api-gateway/agent/v1/agents/{agent_id}
'''
class AgentDeleteYes(TemplateView, RESTfulMethods):

    def get(self, request, *args, **kwargs):
        logger.info('========== Start deleting Agent ==========')
        context = super(AgentDeleteYes, self).get_context_data(**kwargs)
        agent_id = context['agent_id']
        prev_page = context['prev_page']

        api_path = settings.AGENT_DELETE_URL.format(agent_id=agent_id)
        context, status = self._delete_method(api_path=api_path, func_description="Agent Delete", logger=logger)
        logger.info('========== Finished deleting agent ==========')
        if status:
            if prev_page == 'detail' or prev_page == 'update':
                return redirect('agents:agent_detail', agent_id=agent_id)
            else:   # prev_page == 'list'
                return redirect('agents:agent-list')
        else:
            # TODO: add more message in fail case.
            return redirect('agents:agent_delete', agent_id=agent_id)