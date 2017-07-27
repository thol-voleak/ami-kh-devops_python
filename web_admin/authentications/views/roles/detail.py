from authentications.utils import get_auth_header, get_correlation_id_from_username, check_permissions_by_user
from web_admin import api_settings, setup_logger, RestFulClient

from braces.views import GroupRequiredMixin

from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class RoleDetailView(GroupRequiredMixin, TemplateView):
    group_required = "CAN_VIEW_ROLE"
    login_url = 'web:permission_denied'
    raise_exception = False

    template_name = "roles/detail.html"
    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(RoleDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start get role entity ==========')
        context = super(RoleDetailView, self).get_context_data(**kwargs)
        role_id = context['role_id']
        self.logger.info("Searching role with [{}] role id".format(role_id))
        params = {
            'id': role_id
        }
        is_success, status_code, status_message, data = RestFulClient.post(url=api_settings.ROLE_LIST,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger, params=params)
        if is_success:
            context['role'] = data[0]
            self.logger.info('========== End get role entity ==========')
            return context

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers
