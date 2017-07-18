from web_admin.api_settings import AGENT_TYPE_UPDATE_URL, AGENT_TYPE_DETAIL_URL
from web_admin.restful_methods import RESTfulMethods
from web_admin.utils import setup_logger
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class AgentTypeUpdateForm(TemplateView, RESTfulMethods):
    template_name = "agent_type/agent_type_update.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(AgentTypeUpdateForm, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start showing Update Agent Type page ==========')
        try:
            context = super(AgentTypeUpdateForm, self).get_context_data(**kwargs)
            agent_type_id = context['agentTypeId']
            context = self._get_agent_type_detail(agent_type_id)
        except Exception as e:
            self.logger.error(e)
            context = {'agent_type_info': {}}
        self.logger.info('========== Finished showing Update Agent Type page ==========')
        return context

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start updating agent type ==========')

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
            request.session['agent_type_update_msg'] = 'Updated agent type successfully'
            self.logger.info('========== Finished updating agent type ==========')
            return redirect('agent_type:agent-type-detail', agentTypeId=(agent_type_id))
        else:
            params['id'] = agent_type_id
            context = {'agent_type_info': params,
                       'error_msg': data
                      }

            self.logger.info('========== Finished updating agent type ==========')
            return render(request, 'agent_type/agent_type_update.html', context)

    def _get_agent_type_detail(self, agent_type_id):
        data, success = self._get_method(api_path=AGENT_TYPE_DETAIL_URL.format(agent_type_id),
                                         func_description="Agent Type Detail",
                                         logger=logger)
        context = {'agent_type_info': data}
        return context
