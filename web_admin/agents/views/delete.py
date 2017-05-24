import logging

from django.conf import settings
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods

logger = logging.getLogger(__name__)

'''
Author: Steve Le
History:
# 2017-05-23
- Init with basic template name "delete.html"
-- Load Data
'''
class AgentDelete(TemplateView, RESTfulMethods):

    template_name = "agents/delete.html"

    def get_context_data(self, **kwargs):
        try:
            context = super(AgentDelete, self).get_context_data(**kwargs)
            agent_id = context['agent_id']
            prev_page = context['prev_page']

            context, status = self._get_agent_detail(agent_id)
            context.update({'agent_update_msg': self.request.session.pop('agent_update_msg', None)})
            if status:
                agent_type_name, status = self._get_agent_type_name(context['agent']['agent_type_id'])
                if status:
                    context.update({
                        'agent_type_name': agent_type_name
                    })
                else:
                    context.update({
                        'agent_type_name': context.agent.agent_type_id
                    })

            context['prev_page'] = prev_page

            return context
        except:
            context = {'agent': {}}
            return context

        return render(request, self.template_name, context)

    def _get_agent_detail(self, agent_id):
        data, success = self._get_method(api_path=settings.AGENT_DETAIL_PATH.format(agent_id=agent_id),
                                         func_description="Agent detail",
                                         logger=logger)
        context = {
            'agent': data,
            'agent_id': agent_id,
            'msg': self.request.session.pop('agent_registration_msg', None)
        }
        return context, success

    def _get_agent_type_name(self, agent_type_id):
        agent_types_list, success = self._get_method(api_path=settings.AGENT_TYPES_LIST_URL,
                                                     func_description="Agent types list from backend",
                                                     logger=logger,
                                                     is_getting_list=True)
        if success:
            my_id = int(agent_type_id)
            for x in agent_types_list:
                if x['id'] == my_id:
                    agent_type_name = x['name']
                    return agent_type_name, True
            data = 'Unknown', True
        else:
            data = None, False
        return data