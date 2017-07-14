from authentications.utils import get_auth_header
from web_admin import api_settings
from web_admin import setup_logger, RestFulClient
from authentications.apps import InvalidAccessToken
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class PermissionList(TemplateView):
    template_name = "permissions/list.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(PermissionList, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PermissionList, self).get_context_data(**kwargs)
        is_success, status_code, status_message, data = RestFulClient.post(request=self.request,
                                                                           url=api_settings.PERMISSION_LIST,
                                                                           headers=self._get_headers(),
                                                                           logger=logger)
        if is_success:
            self.logger.info("Permissions have [{}] permissions in database".format(len(data)))
            context['permissions'] = data
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
