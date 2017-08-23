from braces.views import GroupRequiredMixin

from agents.views import AgentAPIService

from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import api_settings, setup_logger

import logging

logger = logging.getLogger(__name__)
logging.captureWarnings(True)


class AgentDelete(GroupRequiredMixin, TemplateView, AgentAPIService):
    group_required = "CAN_DELETE_AGENT"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "agents/delete.html"
    get_agent_identity_url = api_settings.GET_AGENT_IDENTITY_URL
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
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
            if status and status_get_agent_identity and status_get_currency:
                if len(agent_identity['agent_identities']) > 0:
                    context.update({
                        'status_get_agent_identity': agent_identity['agent_identities'][0],
                    })

                context.update({
                    'agent_type_name': agent_type_name,
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
