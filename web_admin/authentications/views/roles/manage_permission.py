from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header, get_correlation_id_from_username, check_permissions_by_user
from web_admin import api_settings, setup_logger, RestFulClient

from braces.views import GroupRequiredMixin

from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class ManagePermissionView(GroupRequiredMixin, TemplateView):
    group_required = "CAN_LINK_UNLINK_USERS_BY_ROLE"
    login_url = 'authentications:login'
    raise_exception = False

    template_name = "roles/manage_permission.html"
    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(ManagePermissionView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start get permission entities of role ==========')
        context = super(ManagePermissionView, self).get_context_data(**kwargs)
        role_id = context['role_id']
        params = {
            'role_id': int(role_id)
        }

        is_success_role_perm, status_code_role_perm, status_message_role_perm, data_role_perm = RestFulClient.post(
            url=api_settings.PERMISSION_LIST,
            headers=self._get_headers(),
            loggers=self.logger, params=params)
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
            url=api_settings.PERMISSION_LIST,
            headers=self._get_headers(),
            loggers=self.logger, params=params)

        if (status_code_role_perm == "access_token_expire") or (status_code_role_perm == 'access_token_not_found') or (
                    status_code_role_perm == 'invalid_access_token'):
            self.logger.info("{} for {} username".format(status_message_role_perm, self.request.user))
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

        if len(params_to_delete['permissions']) > 0:
            is_success_delete = self._delete_role_permission(url, params_to_delete)
        if len(params_to_insert['permissions']) > 0:
            is_success_add = self._add_role_permission(role_id, params_to_insert)

        messages.add_message(
            request,
            messages.SUCCESS,
            'Updated data successfully'
        )
        self.logger.info('========== End update permission entities of role ==========')
        return redirect('authentications:role_manage_permission', role_id=role_id)

    def _get_headers(self):
        return get_auth_header(self.request.user)

    def _delete_role_permission(self, url, params_to_delete):
        headers = self._get_headers()
        self.logger.info("Header: [{}]".format(headers))
        is_success_delete, status_code_delete, status_message_delete = RestFulClient.delete(url=url,
                                                                                            headers=headers,
                                                                                            loggers=self.logger,
                                                                                            params=params_to_delete)

        if (status_code_delete == "access_token_expire") or (status_code_delete == 'access_token_not_found') or (
                    status_code_delete == 'invalid_access_token'):
            logger.info("{} for {} username".format(status_message_delete, self.request.user))
            raise InvalidAccessToken(status_message_delete)
        return is_success_delete

    def _add_role_permission(self, role_id, params_to_insert):
        headers = self._get_headers()
        self.logger.info("Header: [{}]".format(headers))
        url = api_settings.ROLE_PERMISSION_PATH.format(role_id=role_id)
        self.logger.info("Adding permission to to [{}] role".format(params_to_insert))
        is_success, status_code, status_message, data = RestFulClient.post(url=url,
                                                                           headers=headers,
                                                                           loggers=self.logger,
                                                                           params=params_to_insert)
        if (status_code == "access_token_expire") or (status_code == 'access_token_not_found') or (
                    status_code == 'invalid_access_token'):
            logger.info("{} for {} username".format(status_message, self.request.user))
            raise InvalidAccessToken(status_message)
        return is_success

    def _get_all_permission(self):
        if getattr(self, '_permissions', None) is None:
            is_success_permissions, status_code_permissions, status_message_permissions, data_permissions = RestFulClient.post(
                url=api_settings.PERMISSION_LIST,
                headers=self._get_headers(),
                loggers=self.logger)
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
