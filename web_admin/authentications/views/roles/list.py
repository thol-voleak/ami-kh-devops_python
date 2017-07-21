from authentications.apps import InvalidAccessToken
from authentications.utils import get_auth_header, get_correlation_id_from_username, check_permissions_by_user
from web_admin import api_settings, setup_logger, RestFulClient

from braces.views import GroupRequiredMixin

from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class RoleList(GroupRequiredMixin, TemplateView):
    group_required = "CAN_SEARCH_ROLE"
    login_url = 'authentications:login'
    raise_exception = False

    template_name = "roles/list.html"
    logger = logger

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
        if is_success:
            self.logger.info("Roles have [{}] role in database".format(len(data)))
            context['roles'] = data
        elif (status_code == "access_token_expire") or (status_code == 'access_token_not_found') or (
                    status_code == 'invalid_access_token'):
            logger.info("{} for {} username".format(status_message, self.request.user))
            raise InvalidAccessToken(status_message)
        return context

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers
