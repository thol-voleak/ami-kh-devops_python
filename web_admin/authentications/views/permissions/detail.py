from authentications.utils import get_auth_header
from web_admin import api_settings
from web_admin import setup_logger, RestFulClient

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class PermissionDetailView(TemplateView):
    template_name = "permissions/detail.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(PermissionDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start get permission entity ==========')
        context = super(PermissionDetailView, self).get_context_data(**kwargs)
        permission_id = context['permission_id']
        is_success, status_code, data = RestFulClient.get(request=self.request,
                                                          url=api_settings.PERMISSION_DETAIL_PATH.format(
                                                              permission_id=permission_id),
                                                          headers=self._get_headers(),
                                                          logger=logger)
        if is_success:
            context['permission'] = data
            self.logger.info('========== End get permission entity ==========')
            return context

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers
