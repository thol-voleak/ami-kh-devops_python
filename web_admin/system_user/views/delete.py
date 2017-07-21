from braces.views import GroupRequiredMixin

from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from web_admin import api_settings, setup_logger
from web_admin.restful_methods import RESTfulMethods
from .system_user_client import SystemUserClient

from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from django.contrib import messages

import logging

logger = logging.getLogger(__name__)


class DeleteView(GroupRequiredMixin, TemplateView, RESTfulMethods):
    group_required = "SYS_CREATE_PERMISSION_ENTITIES"
    login_url = 'authentications:login'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "system_user/delete.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(DeleteView, self).get_context_data(**kwargs)
        system_user_id = context['system_user_id']

        status_code, status_message, data = SystemUserClient.search_system_user(headers=self._get_headers(),
                                                                                logger=self.logger,
                                                                                user_id=system_user_id)
        context = {
            'system_user_info': data[0]
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start deleting system user ==========')

        # Build API Path
        system_user_id = kwargs['system_user_id']
        api_path = api_settings.DELETE_SYSTEM_USER_URL.format(system_user_id)

        # Do Request
        data, status = self._delete_method(
            api_path=api_path,
            func_description="System User Delete"
        )
        self.logger.info('========== Finish deleting system user ==========')
        if status:
            messages.add_message(request, messages.SUCCESS, 'Deleted data successfully')
            return redirect('system_user:system-user-list')
        else:
            logger.info("Error deleting system user {}".format(system_user_id))
