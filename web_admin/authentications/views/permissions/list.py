from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header, get_correlation_id_from_username, check_permissions_by_user
from web_admin import setup_logger, RestFulClient, api_settings

from braces.views import GroupRequiredMixin

from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class PermissionList(GroupRequiredMixin, TemplateView):
    group_required = "SYS_MANAGE_PERMISSION_ENTITIES"
    login_url = 'authentications:login'
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
        is_success, status_code, status_message, data = RestFulClient.post(url=api_settings.PERMISSION_LIST,
                                                                           loggers=self.logger,
                                                                           headers=self._get_headers())
        if is_success:
            self.logger.info("Permissions have [{}] permissions in database".format(len(data)))
            context['permissions'] = data
        else:
            if (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                        status_code == 'invalid_access_token'):
                logger.info("{} for {} username".format(status_message, self.request.user))
                raise InvalidAccessToken(status_message)

        return context

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers
