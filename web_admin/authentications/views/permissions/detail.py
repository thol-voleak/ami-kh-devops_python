from django.contrib import messages

from authentications.utils import get_correlation_id_from_username, get_auth_header, check_permissions_by_user
from authentications.apps import InvalidAccessToken
from web_admin import setup_logger, RestFulClient, api_settings

from braces.views import GroupRequiredMixin

from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class PermissionDetailView(GroupRequiredMixin, TemplateView):
    group_required = "SYS_VIEW_PERMISSION_ENTITIES"
    login_url = 'web:permission_denied'
    raise_exception = False

    template_name = "permissions/detail.html"
    logger = logger

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(PermissionDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start get permission entity ==========')
        context = super(PermissionDetailView, self).get_context_data(**kwargs)
        permission_id = context['permission_id']
        self.logger.info("Searching permission with [{}] id".format(permission_id))
        params = {
            'id': int(permission_id)
        }
        self.logger.info("Searching permission with [{}] id".format(permission_id))
        is_success, status_code, status_message, data = RestFulClient.post(url=api_settings.PERMISSION_LIST,
                                                                           headers=self._get_headers(),
                                                                           loggers=self.logger,
                                                                           params=params)
        if is_success:
            context['permission'] = data[0]
            self.logger.info('========== End get permission entity ==========')
        else:
            if status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                logger.info("{} for {} username".format(status_message, self.request.user))
                raise InvalidAccessToken(status_message)
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
