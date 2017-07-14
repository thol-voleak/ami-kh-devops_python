from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header
from web_admin import api_settings
from web_admin import setup_logger, RestFulClient

from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class ManagePermissionView(TemplateView):
    template_name = "roles/manage_permission.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(ManagePermissionView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start get permission entities of role ==========')
        context = super(ManagePermissionView, self).get_context_data(**kwargs)
        role_id = context['role_id']
        params = {
            'role_id': int(role_id)
        }

        is_success_role_perm, status_code_role_perm, status_message_role_perm, data_role_perm = RestFulClient.post(
            request=self.request,
            url=api_settings.PERMISSION_LIST,
            headers=self._get_headers(),
            logger=logger, params=params)
        if (status_code_role_perm == "access_token_expire") or (status_code_role_perm == 'access_token_not_found') or (
                    status_code_role_perm == 'invalid_access_token'):
            logger.info("{} for {} username".format(status_message_role_perm, self.request.user))
            raise InvalidAccessToken(status_message_role_perm)

        role_permission_id = []
        if len(data_role_perm) > 0:
            role_permission_id = [permission['id'] for permission in data_role_perm]

        data_permissions = self._get_all_permission()

        for permission in data_permissions:
            if permission['id'] in role_permission_id:
                permission['is_granted'] = True
        self.logger.info("Role have permissions [{}]".format(role_permission_id))

        if is_success_role_perm:
            self.logger.info("Got [{}] permission in database".format(len(data_permissions)))
            context['permissions'] = data_permissions
            context['role_permissions'] = data_role_perm

        self.logger.info('========== End get permission entities of role ==========')
        return context

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start update permission entities of role ==========')
        update_roles = request.POST.getlist('roles')

        roles = [int(i) for i in update_roles]
        role_id = kwargs['role_id']
        params = {
            'role_id': int(role_id)
        }
        is_success_role_perm, status_code_role_perm, status_message_role_perm, data_role_perm = RestFulClient.post(
            request=self.request,
            url=api_settings.PERMISSION_LIST,
            headers=self._get_headers(),
            logger=logger, params=params)

        if (status_code_role_perm == "access_token_expire") or (status_code_role_perm == 'access_token_not_found') or (
                    status_code_role_perm == 'invalid_access_token'):
            logger.info("{} for {} username".format(status_message_role_perm, self.request.user))
            raise InvalidAccessToken(status_message_role_perm)

        role_permission_id = [x['id'] for x in data_role_perm]

        permissions_to_insert = [scope for scope in roles if scope not in role_permission_id]
        permissions_to_delete = [scope for scope in role_permission_id if scope not in roles]
        self.logger.info("Delete list permission id [{}]".format(permissions_to_delete))
        self.logger.info("Add list permission id [{}]".format(permissions_to_insert))

        url = api_settings.ROLE_PERMISSION_PATH.format(role_id=role_id)

        params_to_delete = {
            'permissions': permissions_to_delete
        }

        params_to_insert = {
            'permissions': permissions_to_insert
        }

        is_success_delete = self._delete_role_permission(url, logger, params_to_delete)
        is_success_add = self._add_role_permission(url, logger, params_to_insert)

        if is_success_add and is_success_delete:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Updated data successfully'
            )
            self.logger.info('========== End update permission entities of role ==========')
            return redirect('authentications:role_manage_permission', role_id=role_id)

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers

    def _delete_role_permission(self, url, logger, params_to_delete):
        is_success_delete, status_code_delete, status_message_delete = RestFulClient.delete(self.request, url,
                                                                                            self._get_headers(),
                                                                                            logger,
                                                                                            params=params_to_delete)
        if (status_code_delete == "access_token_expire") or (status_code_delete == 'access_token_not_found') or (
                    status_code_delete == 'invalid_access_token'):
            logger.info("{} for {} username".format(status_message_delete, self.request.user))
            raise InvalidAccessToken(status_message_delete)
        return is_success_delete

    def _add_role_permission(self, url, logger, params_to_insert):
        is_success_add, status_code_add, status_message_add, data = RestFulClient.post(self.request, url,
                                                                                       self._get_headers(),
                                                                                       logger, params=params_to_insert)
        if (status_code_add == "access_token_expire") or (status_code_add == 'access_token_not_found') or (
                    status_code_add == 'invalid_access_token'):
            logger.info("{} for {} username".format(status_message_add, self.request.user))
            raise InvalidAccessToken(status_message_add)
        return is_success_add

    def _get_all_permission(self):
        if getattr(self, '_permissions', None) is None:
            is_success_permissions, status_code_permissions, status_message_permissions, data_permissions = RestFulClient.post(
                request=self.request,
                url=api_settings.PERMISSION_LIST,
                headers=self._get_headers(),
                logger=logger)
            if (status_code_permissions == "access_token_expire") or (
                        status_code_permissions == 'access_token_not_found') or (
                        status_code_permissions == 'invalid_access_token'):
                logger.info("{} for {} username".format(status_message_permissions, self.request.user))
                raise InvalidAccessToken(status_message_permissions)

            if is_success_permissions:
                self._permissions = data_permissions
            else:
                self._permissions = []
        return self._permissions
