from web_admin.restful_methods import RESTfulMethods
from web_admin.api_settings import AGENT_TYPE_CREATE_URL

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class AgentTypeCreate(TemplateView, RESTfulMethods):
    template_name = "agent_type/create_agent_type.html"

    def get_context_data(self, **kwargs):
        context = super(AgentTypeCreate, self).get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        logger.info('========== Start create agent type ==========')
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
                return redirect('agent_type:agent-type-list')
            else:
                context = {
                    'client_info': params,
                    'error_msg': 'Something went wrong.'
                }
                logger.info('========== End create agent type ==========')
                return render(request, 'agent_type/agent_types_list.html', context)
        except Exception as e:
            logger.info(e)
            client_info = {
                "client_id": settings.CLIENTID,
                "client_secret": settings.CLIENTSECRET
            }
            context = {'client_info': client_info}
            return render(request, 'agent_type/agent_types_list.html', context)
