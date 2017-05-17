import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views import View
from web_admin.restful_methods import RESTfulMethods

logger = logging.getLogger(__name__)


class DeleteView(TemplateView, RESTfulMethods):
    template_name = "agent_type/agent_type_delete.html"

    def get_context_data(self, **kwargs):
        try:
            logger.info('========== Start getting agent type detail ==========')
            context = super(DeleteView, self).get_context_data(**kwargs)
            agent_type_id = context['agent_type_id']

            return self._get_agent_type_detail(agent_type_id)
        except:
            context = {'agent_type_info': {}}
            return context

    def _get_agent_type_detail(self, agent_type_id):
        data, success = self._get_method(api_path=settings.AGENT_TYPE_DETAIL_URL.format(agent_type_id),
                                                     func_description="Agent Type",
                                                     logger=logger)
        return {'agent_type_info': data}

class DeleteCommand(View, RESTfulMethods):
    def post(self, request, *args, **kwargs):
        logger.info("tuong======")
        agent_type_id = kwargs['agent_type_id']

        data, success = self._delete_method(api_path=settings.DELETE_AGENT_TYPE_URL.format(agent_type_id),
                                            func_description="Balance Distribution",
                                            logger=logger)
        if success:
            request.session['agent_type_delete_msg'] = 'Deleted data successfully'
            return HttpResponseRedirect(reverse('agent_type:agent-type-list', args=(None)))
        else:
            raise Exception("Something went wrong.")

        return success