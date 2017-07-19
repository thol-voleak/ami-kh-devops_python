from authentications.utils import get_correlation_id_from_username, get_auth_header
from web_admin import setup_logger, RestFulClient, api_settings
from authentications.apps import InvalidAccessToken

from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class PermissionDetailView(TemplateView):
    template_name = "permissions/detail.html"
    logger = logger

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
            if (status_code == "access_token_expire") or (status_code == 'access_token_not_found') or (
                        status_code == 'invalid_access_token'):
                logger.info("{} for {} username".format(status_message, self.request.user))
                raise InvalidAccessToken(status_message)
        return context

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers
