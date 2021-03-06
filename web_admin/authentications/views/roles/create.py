from braces.views import GroupRequiredMixin

from authentications.utils import get_correlation_id_from_username, get_auth_header, check_permissions_by_user
from authentications.views.roles_client import RolesClient
from web_admin import api_settings
from web_admin import setup_logger, RestFulClient


from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView

import logging


logger = logging.getLogger(__name__)


class RoleCreate(GroupRequiredMixin, TemplateView):
    template_name = "roles/create.html"
    logger = logger

    group_required = "CAN_CREATE_ROLE"
    login_url = 'web:permission_denied'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(RoleCreate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(RoleCreate, self).get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start creating role ==========')

        name = request.POST.get('name', '')
        description = request.POST.get('description', '')

        params = {
            'name': name,
            'description': description,
            'is_page_level': True
        }

        is_success, status_code, status_message, data = RolesClient.create_role(
            headers=self._get_headers(), params=params, logger=self.logger
        )

        if is_success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Created role entity successfully'
            )
            self.logger.info('========== End creating role ==========')
            return redirect('authentications:role_list')
        else:
            messages.add_message(
                request,
                messages.ERROR,
                status_message
            )
            self.logger.error('========== End creating role got error [{}] =========='.format(status_message))
            return render(request, self.template_name)

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers
