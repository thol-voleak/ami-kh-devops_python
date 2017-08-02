from authentications.utils import get_correlation_id_from_username, get_auth_header, check_permissions_by_user
from authentications.views.permissions_client import PermissionsClient
from web_admin import setup_logger, RestFulClient, api_settings

from braces.views import GroupRequiredMixin

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from authentications.apps import InvalidAccessToken

import logging

logger = logging.getLogger(__name__)


class PermissionCreate(GroupRequiredMixin, TemplateView):
    group_required = "SYS_CREATE_PERMISSION_ENTITIES"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    template_name = "permissions/create.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(PermissionCreate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PermissionCreate, self).get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start creating permission ==========')

        name = request.POST.get('name', '')
        description = request.POST.get('description', '')

        params = {
            'name': name,
            'description': description,
            'is_page_level': True
        }

        is_success, status_code, status_message, data = PermissionsClient.create_permission(headers=self._get_headers(),
                                                                                            params=params,
                                                                                            logger=self.logger)
        if is_success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Added data successfully'
            )
            self.logger.info('========== End creating permission ==========')
            return redirect('authentications:permissions_list')
        else:
            messages.add_message(
                request,
                messages.ERROR,
                status_message
            )
            return render(request, self.template_name)

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers
