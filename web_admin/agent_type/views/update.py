from braces.views import GroupRequiredMixin

from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.api_settings import AGENT_TYPE_UPDATE_URL, AGENT_TYPE_DETAIL_URL
from web_admin.restful_methods import RESTfulMethods
from web_admin import setup_logger

from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class AgentTypeUpdateForm(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_EDIT_AGENT_TYPE"
    login_url = 'web:web-index'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "agent_type/agent_type_update.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
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
        body = {"id" : agent_type_id}
        data, success = self._post_method(api_path=AGENT_TYPE_DETAIL_URL.format(agent_type_id),
                                         func_description="Agent Type Detail",
                                         logger=logger,
                                         params=body)
        context = {'agent_type_info': data[0]}
        return context
