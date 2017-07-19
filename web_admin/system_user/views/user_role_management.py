from authentications.utils import get_correlation_id_from_username, get_auth_header
from web_admin import setup_logger, RestFulClient, api_settings

from django.contrib import messages
from django.shortcuts import render
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class RoleManagementView(TemplateView):
    template_name = "system_user/user_role_management.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(RoleManagementView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start get all role entities ==========')
        context = super(RoleManagementView, self).get_context_data(**kwargs)
        system_user_id = context['system_user_id']
        params = {
            'system_user_id': int(system_user_id)
        }

        self.logger.info('========== End get all role entities ==========')

        context['user_role'] = self.get_user_role(system_user_id)
        context['roles'] = self.get_roles()
        return context

    def post(self, request, *args, **kwargs):
        context = {}
        system_user_id = kwargs['system_user_id']

        role_id = request.POST.get('role', None)

        context['system_user_id'] = system_user_id
        context['roles'] = self.get_roles()

        user_role = self.get_user_role(logger, system_user_id)
        if len(user_role) > 0:
            if user_role['id'] != role_id:
                is_success_delete = self._delete_user_role(user_role['id'], system_user_id)
                is_success_add = self._add_user_role(role_id, system_user_id)
                if is_success_delete and is_success_add:
                    messages.add_message(
                        request,
                        messages.SUCCESS,
                        'Updated data successfully'
                    )
        else:
            is_success_add = self._add_user_role(role_id, system_user_id)
            if is_success_add:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'Updated data successfully'
                )

        context['user_role'] = self.get_user_role(system_user_id)
        context['roles'] = self.get_roles()

        return render(request, self.template_name, context)

    def get_roles(self):
        is_success, status_code, status_message, data = RestFulClient.post(url=api_settings.ROLE_LIST,
                                                                           headers=self._get_headers(),
                                                                           logger=self.logger)

        self.logger.info("Have {} roles in database".format(len(data)))

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
            if len(data) > 0:
                return data[0]
            else:
                return {}
        else:
            return []

    def _delete_user_role(self, role_id, user_id):
        url = api_settings.ROLE_USER_PATH.format(user_id=user_id)
        params = {
            'role_id': int(role_id)
        }
        is_success_delete, status_code_delete, status_message_delete = RestFulClient.delete(url,
                                                                                            self._get_headers(),
                                                                                            self.logger,
                                                                                            params=params)
        return is_success_delete

    def _add_user_role(self, role_id, user_id):
        url = api_settings.USER_ROLE_PATH.format(role_id=role_id)
        params = {
            'user_id': int(user_id)
        }
        is_success_add, status_code_add, status_message_add, data = RestFulClient.post(url,
                                                                                       self._get_headers(),
                                                                                       self.logger,
                                                                                       params=params)
        return is_success_add

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers
