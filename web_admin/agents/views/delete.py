from agents.views import AgentAPIService
from web_admin import api_settings

from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
from web_admin.utils import setup_logger
from web_admin.restful_methods import RESTfulMethods
from web_admin import api_settings



import logging


logger = logging.getLogger(__name__)


class AgentDelete(TemplateView, AgentAPIService):
    template_name = "agents/delete.html"
    get_agent_identity_url = "api-gateway/agent/v1/agents/{agent_id}/identities"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(AgentDelete, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = super(AgentDelete, self).get_context_data(**kwargs)
        agent_id = context['agent_id']

        api_path = api_settings.AGENT_DELETE_URL.format(agent_id=agent_id)
        context, status = self._delete_method(api_path=api_path, func_description="Agent Delete", logger=logger)

        if status:
            previous_page = request.POST.get('previous_page')
            if previous_page is not None:

                # Forward update case to detail after execute delete action.
                if "update" in previous_page:
                    previous_page = previous_page.replace('update/', '', 1)

                request.session['agent_update_msg'] = 'Deleted data successfully'

                return HttpResponseRedirect(previous_page)
            else:
                redirect('agents:agent-list')
        else:
            # TODO: add more message in fail case.
            return redirect('agents:agent_delete', agent_id=agent_id)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start showing Delete Agent page ==========')
        context = super(AgentDelete, self).get_context_data(**kwargs)
        agent_id = context['agent_id']

        context, status = self.get_agent_detail(agent_id)
        agent_identity, status_get_agent_identity = self.get_agent_identity(agent_id)
        currencies, status_get_currency = self.get_currencies(agent_id)

        context.update({'agent_update_msg': self.request.session.pop('agent_update_msg', None)})
        if status and status_get_agent_identity and status_get_currency:
            agent_type_name, status = self.get_agent_type_name(context['agent']['agent_type_id'])
            if status:
                context.update({
                    'agent_type_name': agent_type_name,
                    'status_get_agent_identity': agent_identity['agent_identities'][0],
                    'currencies': currencies
                })
            else:
                context.update({
                    'agent_type_name': context.agent.agent_type_id
                })
            self.logger.info('========== Finished showing Delete Agent page ==========')
            return context
        else:
            context = {'agent': {}}
            self.logger.info('========== Finished showing Delete Agent page ==========')
            return context
