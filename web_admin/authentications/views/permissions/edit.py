from authentications.utils import get_correlation_id_from_username, get_auth_header, check_permissions_by_user
from authentications.views.permissions_client import PermissionsClient
from web_admin import setup_logger, RestFulClient, api_settings
from authentications.apps import InvalidAccessToken

from braces.views import GroupRequiredMixin

from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class PermissionEditView(GroupRequiredMixin, TemplateView):
    group_required = "SYS_EDIT_PERMISSION_ENTITIES"
    login_url = 'web:permission_denied'
    raise_exception = False

    template_name = "permissions/edit.html"
    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(PermissionEditView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start get permission entity ==========')
        context = super(PermissionEditView, self).get_context_data(**kwargs)
        permission_id = context['permission_id']

        params = {
            'id': int(permission_id)
        }
        self.logger.info("Searching permission with [{}] id".format(permission_id))

        is_success, status_code, status_message, permission_detail = PermissionsClient.get_permission_detail(
            headers=self._get_headers(), params=params, logger=self.logger
        )

        if is_success:
            context['permission'] = permission_detail
        else:
            messages.error(self.request, status_message)
        self.logger.info('========== End get permission entity ==========')
        return context

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start update permission entity ==========')
        permission_id = kwargs['permission_id']

        name = request.POST.get('name', '')
        description = request.POST.get('description', '')

        params = {
            'name': name,
            'description': description,
            'is_page_level': True
        }

        is_success, status_code, status_message, data = PermissionsClient.update_permission(
            permission_id=permission_id, headers=self._get_headers(), params=params, logger=self.logger
        )

        if is_success:
            messages.success(self.request, 'Updated data successfully')
        else:
            messages.error(self.request, status_message)
        self.logger.info('========== End update permission entity ==========')
        return redirect('authentications:permissions_list')

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers
