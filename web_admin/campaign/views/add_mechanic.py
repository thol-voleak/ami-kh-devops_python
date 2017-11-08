from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin.restful_methods import RESTfulMethods
from web_admin.api_settings import AGENT_TYPE_CREATE_URL
from web_admin import setup_logger

from braces.views import GroupRequiredMixin

from django.conf import settings
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class AddMechanic(GroupRequiredMixin, TemplateView):
    group_required = "CAN_VIEW_CAMPAIGN_DETAILS"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "campaign/add_mechanic.html"
    logger = logger

    permission_required = "auth.change_user"
    login_url = settings.LOGIN_URL
    raise_exception = False

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(AddMechanic, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start showing Add Mechanic page ==========')
        context = super(AddMechanic, self).get_context_data(**kwargs)
        self.logger.info('========== Finished showing Add Mechanic page ==========')
        return context

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start adding Mechanic ==========')
        params = {
            "name": request.POST.get('agent_type_input'),
            "description": request.POST.get('agent_type_description_input'),
        }

        data, success = self._post_method(api_path=AGENT_TYPE_CREATE_URL,
                                          func_description="Agent Type",
                                          logger=logger, params=params)
        if success:
            request.session['agent_type_create_msg'] = 'Added data successfully'
            self.logger.info('========== Finished adding Mechanic ==========')
            return redirect('agent_type:agent-type-list')
        else:
            context = {
                'agent_type_info': params,
                'error_msg': data
            }
            self.logger.info('========== Finished creating agent type ==========')
            return render(request, 'agent_type/create_agent_type.html', context)
