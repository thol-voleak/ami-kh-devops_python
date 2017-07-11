from authentications.utils import get_auth_header
from web_admin import api_settings
from web_admin import setup_logger, RestFulClient

from django.contrib import messages
from django.shortcuts import render
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class RoleManagementView(TemplateView):
    template_name = "system_user/user_role_management.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(RoleManagementView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start get all role entities ==========')
        context = super(RoleManagementView, self).get_context_data(**kwargs)
        system_user_id = context['system_user_id']
        params = {
            'system_user_id': int(system_user_id)
        }

        self.logger.info('========== End get all role entities ==========')

        context['user_role'] = self.get_user_role(logger, system_user_id)
        context['roles'] = self.get_roles(logger)
        return context

    def post(self, request, *args, **kwargs):
        context = {}
        system_user_id = kwargs['system_user_id']

        role_id = request.POST.get('role', '')

        context['system_user_id'] = system_user_id
        context['roles'] = self.get_roles(logger)

        user_role = self.get_user_role(logger, system_user_id)
        if user_role['id'] != role_id:
            is_success_delete = self._delete_user_role(logger, user_role['id'], system_user_id)
            is_success_add = self._add_user_role(logger, role_id, system_user_id)
            if is_success_delete and is_success_add:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'Updated data successfully'
                )

        context['user_role'] = self.get_user_role(logger, system_user_id)
        context['roles'] = self.get_roles(logger)

        return render(request, self.template_name, context)

    def get_roles(self, logger):
        is_success, status_code, status_message, data = RestFulClient.post(request=self.request,
                                                                           url=api_settings.ROLE_LIST,
                                                                           headers=self._get_headers(),
                                                                           logger=logger)

        self.logger.info("Roles have {} role in database".format(len(data)))

        if is_success:
            return data
        else:
            return []

    def get_user_role(self, logger, user_id):
        params = {
            'user_id': user_id
        }
        is_success, status_code, status_message, data = RestFulClient.post(request=self.request,
                                                                           url=api_settings.ROLE_LIST,
                                                                           headers=self._get_headers(),
                                                                           logger=logger, params=params)

        self.logger.info("User have {} role id".format(data))
        if is_success:
            return data[0]
        else:
            return []

    def _delete_user_role(self, logger, role_id, user_id):
        url = api_settings.ROLE_USER_PATH.format(user_id=user_id)
        params = {
            'role_id': int(role_id)
        }
        is_success_delete, status_code_delete, status_message_delete = RestFulClient.delete(self.request, url,
                                                                                            self._get_headers(),
                                                                                            logger,
                                                                                            params=params)
        return is_success_delete

    def _add_user_role(self, logger, role_id, user_id):
        url = api_settings.USER_ROLE_PATH.format(role_id=role_id)
        params = {
            'user_id': int(user_id)
        }
        is_success_add, status_code_add, status_message_add, data = RestFulClient.post(self.request, url,
                                                                                       self._get_headers(),
                                                                                       logger, params=params)
        return is_success_add

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers
