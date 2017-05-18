import logging

from django.conf import settings
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods

logger = logging.getLogger(__name__)


class AgentTypeUpdateForm(TemplateView, RESTfulMethods):
    template_name = "agent_type/agent_type_update.html"

    def get_context_data(self, **kwargs):
        try:
            context = super(AgentTypeUpdateForm, self).get_context_data(**kwargs)
            agent_type_id = context['agentTypeId']

            return self._get_agent_type_detail(agent_type_id)
        except:
            context = {'agent_type_info': {}}
            return context

    def _get_agent_type_detail(self, agent_type_id):
        data, success = self._get_method(api_path=settings.AGENT_TYPE_UPDATE_URL.format(agent_type_id),
                                         func_description="Agent Type Detail",
                                         logger=logger)
        context = {'agent_type_info': data}
        return context

class AgentTypeUpdate(View, RESTfulMethods):
    def post(self, request, *args, **kwargs):
        agent_type_id = kwargs['agentTypeId']
        name = request.POST.get('agent_type_input')
        description = request.POST.get('agent_type_description_input')
        params = {
            "name": name,
            "description": description,
        }
        data, success = self._put_method(api_path=settings.AGENT_TYPE_UPDATE_URL.format(agent_type_id),
                                          func_description="Agent Type",
                                          logger=logger, params=params)
        if success:
            request.session['agent_type_update_msg'] = 'Updated agent type successfully'
            return redirect('agent_type:agent-type-detail', agentTypeId=(agent_type_id))
        else:
            context = {'agent_type_info': params}
            return render(request, 'agent_type/agent_type_update.html', context)