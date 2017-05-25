from web_admin.restful_methods import RESTfulMethods
from web_admin.api_settings import AGENT_TYPE_DETAIL_URL, DELETE_AGENT_TYPE_URL

from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.views import View
from django.urls import reverse

import logging

logger = logging.getLogger(__name__)


class DeleteView(TemplateView, RESTfulMethods):
    template_name = "agent_type/agent_type_delete.html"

    def get_context_data(self, **kwargs):
        logger.info('========== Start showing Delete Agent Type page ==========')
        try:
            context = super(DeleteView, self).get_context_data(**kwargs)
            agent_type_id = context['agent_type_id']
            logger.info('========== Finished showing Delete Agent Type page ==========')
            return self._get_agent_type_detail(agent_type_id)
        except Exception as e:
            logger.error(e)
            context = {}
            logger.info('========== Finished showing Delete Agent Type page ==========')
            return context

    def post(self, request, *args, **kwargs):
        logger.info('========== Start deleting agent type ==========')
        agent_type_id = kwargs['agent_type_id']

        data, success = self._delete_method(api_path=DELETE_AGENT_TYPE_URL.format(agent_type_id),
                                            func_description="Balance Distribution",
                                            logger=logger)
        if success:
            request.session['agent_type_delete_msg'] = 'Deleted data successfully'
            logger.info('========== Finished deleting agent type ==========')
            return HttpResponseRedirect(reverse('agent_type:agent-type-list'))
        else:
            logger.info('========== Finished deleting agent type ==========')
            raise Exception("Something went wrong.")
        return success

    def _get_agent_type_detail(self, agent_type_id):
        data, success = self._get_method(api_path=AGENT_TYPE_DETAIL_URL.format(agent_type_id),
                                         func_description="Agent Type",
                                         logger=logger)
        return {'agent_type_info': data}
