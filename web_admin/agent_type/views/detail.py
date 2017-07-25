from braces.views import GroupRequiredMixin

from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.api_settings import AGENT_TYPE_DETAIL_URL
from web_admin.restful_methods import RESTfulMethods
from web_admin import setup_logger

from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class DetailView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "CAN_DELETE_AGENT_TYPE"
    login_url = 'web:web-index'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "agent_type/agent_type_detail.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start showing Agent Type Detail page ==========')
        context = super(DetailView, self).get_context_data(**kwargs)
        agent_type_id = context['agentTypeId']
        params = {"id": agent_type_id}
        data, success = self._post_method(AGENT_TYPE_DETAIL_URL, func_description="", logger=logger, params=params,
                                          only_return_data=True)
        if success:
            context = {
                'agent_type_info': data[0],
                'msg': self.request.session.pop('agent_type_update_msg', None)
            }
        else:
            context = {
                'agent_type_info': {},
                'msg': self.request.session.pop('agent_type_update_msg', None)
            }

        self.logger.info('========== Finished showing Agent Type Detail page ==========')
        return context
