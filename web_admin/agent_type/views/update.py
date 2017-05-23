from web_admin.api_settings import AGENT_TYPE_UPDATE_URL
from web_admin.restful_methods import RESTfulMethods

from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class AgentTypeUpdateForm(TemplateView, RESTfulMethods):
    template_name = "agent_type/agent_type_update.html"

    def get_context_data(self, **kwargs):
        try:
            context = super(AgentTypeUpdateForm, self).get_context_data(**kwargs)
            agent_type_id = context['agentTypeId']

            return self._get_agent_type_detail(agent_type_id)
        except Exception as e:
            logger.error(e)
            context = {'agent_type_info': {}}
            return context

    def post(self, request, *args, **kwargs):
        logger.info('========== Start update agent type detail ==========')

        name = request.POST.get('agent_type_input')
        description = request.POST.get('agent_type_description_input')
        agent_type_id = kwargs['agentTypeId']

        params = {
            "name": name,
            "description": description,
        }
        data, success = self._put_method(api_path=AGENT_TYPE_UPDATE_URL.format(agent_type_id),
                                         func_description="Agent Type",
                                         logger=logger, params=params)
        if success:
            logger.info('========== End update agent type detail ==========')
            request.session['agent_type_update_msg'] = 'Updated agent type successfully'
            return redirect('agent_type:agent-type-detail', agentTypeId=(agent_type_id))
        else:
            context = {'agent_type_info': params}
            return render(request, 'agent_type/agent_type_update.html', context)

    def _get_agent_type_detail(self, agent_type_id):
        data, success = self._get_method(api_path=AGENT_TYPE_UPDATE_URL.format(agent_type_id),
                                         func_description="Agent Type Detail",
                                         logger=logger)
        context = {'agent_type_info': data}
        return context
