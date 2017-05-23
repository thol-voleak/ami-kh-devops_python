import logging

from django.conf import settings
from django.shortcuts import redirect, render
from django.views import View
from web_admin.restful_methods import RESTfulMethods

logger = logging.getLogger(__name__)


class AgentTypeCreate(View, RESTfulMethods):
    def get(self, request, *args, **kwargs):
        agent_type_info = {
            "agent_type_input": None,
            "agent_type_description_input": None,
        }
        context = {'agent_type_info': agent_type_info,
                   'error_msg': None}

        return render(request, 'agent_type/create_agent_type.html', context)

    def post(self, request, *args, **kwargs):
        try:
            params = {
                "name": request.POST.get('agent_type_input'),
                "description": request.POST.get('agent_type_description_input'),
            }
            data, success = self._post_method(api_path=settings.AGENT_TYPE_CREATE_URL,
                                              func_description="Agent Type",
                                              logger=logger, params=params)
            if success:
                request.session['agent_type_create_msg'] = 'Added data successfully'
                return redirect('agent_type:agent-type-list')
            else:
                context = {'client_info': params,
                           'error_msg': 'Something went wrong.'}
                return render(request, 'agent_type/agent_types_list.html', context)
        except Exception as e:
            logger.info(e)
            client_info = {
                "client_id": settings.CLIENTID,
                "client_secret": settings.CLIENTSECRET,
                "agent_type_input": None,
                "agent_type_description_input": None,
            }
            context = {'client_info': client_info, 'error_msg': None}
            return render(request, 'agent_type/agent_types_list.html', context)