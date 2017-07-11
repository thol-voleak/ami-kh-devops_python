from authentications.utils import get_auth_header
from web_admin import api_settings
from web_admin import setup_logger, RestFulClient

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class RoleDeleteView(TemplateView):
    template_name = "roles/delete.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(RoleDeleteView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start get role entity ==========')
        context = super(RoleDeleteView, self).get_context_data(**kwargs)
        role_id = context['role_id']
        is_success, status_code, data = RestFulClient.get(request=self.request,
                                                          url=api_settings.ROLE_DETAIL_PATH.format(
                                                              role_id=role_id),
                                                          headers=self._get_headers(),
                                                          logger=logger)
        if is_success:
            context['role'] = data
            self.logger.info('========== End get role entity ==========')
            return context

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start delete role entity ==========')
        role_id = kwargs['role_id']
        url = api_settings.ROLE_DETAIL_PATH.format(role_id=role_id)

        is_success, status_code, status_message = RestFulClient.delete(self.request, url, self._get_headers(),
                                                                       logger)

        if is_success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Deleted role entity successfully'
            )
            self.logger.info('========== End delete role entity ==========')
            return redirect('authentications:role_list')

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers
