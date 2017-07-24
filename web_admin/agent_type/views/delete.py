from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.restful_methods import RESTfulMethods
from web_admin.api_settings import AGENT_TYPE_DETAIL_URL, DELETE_AGENT_TYPE_URL
from web_admin import setup_logger
from django.shortcuts import render
from braces.views import GroupRequiredMixin

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import TemplateView
import logging

logger = logging.getLogger(__name__)


class DeleteView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_DELETE_AGENT_TYPE"
    login_url = 'authentications:login'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "agent_type/agent_type_delete.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start showing Delete Agent Type page ==========')
        try:
            context = super(DeleteView, self).get_context_data(**kwargs)
            agent_type_id = context['agent_type_id']  
            self.logger.info('========== Finished showing Delete Agent Type page ==========')          
            return self._get_agent_type_detail(agent_type_id)
        except Exception as e:
            self.logger.error(e)
            context = {}
            self.logger.info('========== Finished showing Delete Agent Type page ==========')
            return context

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start deleting agent type ==========')
        agent_type_id = kwargs['agent_type_id']

        data, success = self._delete_method(api_path=DELETE_AGENT_TYPE_URL.format(agent_type_id),
                                            func_description="Delete agent type",
                                            logger=logger)
        if success:
            request.session['agent_type_delete_msg'] = 'Deleted data successfully'
            self.logger.info('========== Finished deleting agent type ==========')
            return HttpResponseRedirect(reverse('agent_type:agent-type-list'))
        else:
            context = self._get_agent_type_detail(agent_type_id)
            self.logger.info('========== Finished deleting agent type ==========')
            context.update({
                'msg':'Something wrong happen',
            })
            return render(request, self.template_name, context)
        return success

    def _get_agent_type_detail(self, agent_type_id):
        param = {'id': agent_type_id}
        data, success = self._post_method(api_path=AGENT_TYPE_DETAIL_URL,
                                         func_description="Agent Type",
                                         logger=logger,
                                         params = param)
        return {'agent_type_info': data[0]}
