from authentications.utils import get_auth_header
from web_admin import api_settings
from web_admin import setup_logger, RestFulClient

from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class RoleList(TemplateView):
    template_name = "roles/list.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(RoleList, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(RoleList, self).get_context_data(**kwargs)
        is_success, status_code, status_message, data = RestFulClient.post(request=self.request,
                                                                           url=api_settings.ROLE_LIST,
                                                                           headers=self._get_headers(),
                                                                           logger=logger)
        if is_success:
            self.logger.info("Roles have [{}] role in database".format(len(data)))
            context['roles'] = data
        return context

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers
