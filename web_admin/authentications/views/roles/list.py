from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header, get_correlation_id_from_username, check_permissions_by_user
from web_admin import api_settings, setup_logger, RestFulClient

from braces.views import GroupRequiredMixin

from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class RoleList(GroupRequiredMixin, TemplateView):
    template_name = "roles/list.html"
    logger = logger

    group_required = "CAN_MANAGE_ROLE"
    login_url = 'web:web-index'
    raise_exception = False

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(RoleList, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(RoleList, self).get_context_data(**kwargs)
        is_success, status_code, status_message, data = RestFulClient.post(url=api_settings.ROLE_LIST,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger)
        permissions = {}
        permissions['is_permission_detail'] = check_permissions_by_user(self.request.user, 'CAN_VIEW_ROLE')
        permissions['is_permission_edit'] = check_permissions_by_user(self.request.user, 'CAN_EDIT_ROLE')
        permissions['is_permission_delete'] = check_permissions_by_user(self.request.user, 'CAN_DELETE_ROLE')
        permissions['is_permission_manage'] = check_permissions_by_user(self.request.user, 'CAN_MANAGE_PERM_FOR_ROLE')

        if is_success:
            self.logger.info("Roles have [{}] role in database".format(len(data)))
            context['roles'] = data
            context['permissions'] = permissions
        elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                    status_code == 'invalid_access_token'):
            logger.info("{} for {} username".format(status_message, self.request.user))
            raise InvalidAccessToken(status_message)
        return context

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers
