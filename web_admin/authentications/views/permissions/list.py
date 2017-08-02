from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header, get_correlation_id_from_username, check_permissions_by_user
from authentications.views.permissions_client import PermissionsClient
from web_admin import setup_logger, RestFulClient, api_settings

from braces.views import GroupRequiredMixin

from django.contrib import messages
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class PermissionList(GroupRequiredMixin, TemplateView):
    group_required = "SYS_MANAGE_PERMISSION_ENTITIES"
    login_url = 'web:permission_denied'
    raise_exception = False

    template_name = "permissions/list.html"
    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(PermissionList, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PermissionList, self).get_context_data(**kwargs)

        is_success, status_code, status_message, permissions = PermissionsClient.get_permissions(
            headers=self._get_headers(), params={}, logger=self.logger)

        if is_success:
            page_permissions_list = self._check_permission_list_page()
            self.logger.info("Permissions have [{}] permissions in database".format(len(permissions)))
            context['permissions'] = permissions
            context['page_permissions_list'] = page_permissions_list
        else:
            messages.add_message(
                self.request,
                messages.ERROR,
                status_message
            )
        return context

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers

    def _check_permission_list_page(self):
        self.logger.info("Checking permission for permission entities page")
        return {
            "sys_view_permission_entities":
                check_permissions_by_user(self.request.user, 'SYS_VIEW_PERMISSION_ENTITIES'),
            "sys_edit_permission_entities":
                check_permissions_by_user(self.request.user, 'SYS_EDIT_PERMISSION_ENTITIES'),
            "sys_delete_permission_entities":
                check_permissions_by_user(self.request.user, 'SYS_DELETE_PERMISSION_ENTITIES')
        }
