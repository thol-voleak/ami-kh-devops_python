from authentications.utils import get_correlation_id_from_username
from web_admin import api_settings, setup_logger
from web_admin.restful_methods import RESTfulMethods
from .system_user_client import SystemUserClient

from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from django.contrib import messages

import logging

logger = logging.getLogger(__name__)


class DeleteView(TemplateView, RESTfulMethods):
    template_name = "system_user/delete.html"

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = super(DeleteView, self).get_context_data(**kwargs)
        system_user_id = context['system_user_id']

        status_code, status_message, data = SystemUserClient.search_system_user(self.request, self._get_headers(),
                                                                                logger, None, None, system_user_id)

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
            func_description="System User Delete",
            logger=logger
        )
        self.logger.info('========== Finish deleting system user ==========')
        if status:
            messages.add_message(request, messages.SUCCESS, 'Deleted data successfully')
            return redirect('system_user:system-user-list')
        else:
            logger.info("Error deleting system user {}".format(system_user_id))
