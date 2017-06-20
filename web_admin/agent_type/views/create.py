from web_admin.restful_methods import RESTfulMethods
from web_admin.api_settings import AGENT_TYPE_CREATE_URL
from web_admin.utils import setup_logger
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class AgentTypeCreate(TemplateView, RESTfulMethods):
    template_name = "agent_type/create_agent_type.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(AgentTypeCreate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start showing Create Agent Type page ==========')
        context = super(AgentTypeCreate, self).get_context_data(**kwargs)
        self.logger.info('========== Finished showing Create Agent Type page ==========')
        return context

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start creating agent type ==========')
        try:
            params = {
                "name": request.POST.get('agent_type_input'),
                "description": request.POST.get('agent_type_description_input'),
            }

            data, success = self._post_method(api_path=AGENT_TYPE_CREATE_URL,
                                              func_description="Agent Type",
                                              logger=logger, params=params)
            if success:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'Added data successfully'
                )
                self.logger.info('========== Finished creating agent type ==========')
                return redirect('agent_type:agent-type-list')
            else:
                context = {
                    'client_info': params,
                    'error_msg': 'Something went wrong.'
                }
                self.logger.info('========== Finished creating agent type ==========')
                return render(request, 'agent_type/agent_types_list.html', context)
        except Exception as e:
            self.logger.info(e)
            client_info = {
                "client_id": settings.CLIENTID,
                "client_secret": settings.CLIENTSECRET
            }
            context = {'client_info': client_info}
            self.logger.info('========== Finished creating agent type ==========')
            return render(request, 'agent_type/agent_types_list.html', context)
