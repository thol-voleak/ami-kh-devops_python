import logging
from web_admin import api_settings
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods
from web_admin.utils import setup_logger


logger = logging.getLogger(__name__)

class DetailView(TemplateView, RESTfulMethods):
    template_name = "agents/detail.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(DetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start showing Agent Detail page ==========')
        try:
            context = super(DetailView, self).get_context_data(**kwargs)
            agent_id = context['agent_id']

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
            self.logger.info('========== Finished showing Agent Detail page ==========')
            return context
        except:
            context = {'agent': {}}
            self.logger.info('========== Finished showing Agent Detail page ==========')
            return context

    def _get_agent_detail(self, agent_id):
        data, success = self._get_method(api_path=api_settings.AGENT_DETAIL_PATH.format(agent_id=agent_id),
                                         func_description="Agent detail",
                                         logger=logger)
        context = {
            'agent': data,
            'agent_id': agent_id,
            'msg': self.request.session.pop('agent_registration_msg', None)
        }
        return context, success
    
    def _get_agent_type_name(self, agent_type_id):
        agent_types_list, success = self._get_method(api_path=api_settings.AGENT_TYPES_LIST_URL,
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