from authentications.utils import get_auth_header
from web_admin import api_settings
from web_admin import setup_logger, RestFulClient

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class RoleEditView(TemplateView):
    template_name = "roles/edit.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(RoleEditView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start get role entity ==========')
        context = super(RoleEditView, self).get_context_data(**kwargs)
        role_id = context['role_id']
        self.logger.info("Searching role with [{}] role id".format(role_id))
        params = {
            'id': role_id
        }
        is_success, status_code, status_message, data = RestFulClient.post(request=self.request,
                                                                           url=api_settings.ROLE_LIST,
                                                                           headers=self._get_headers(),
                                                                           logger=logger, params=params)
        if is_success:
            context['role'] = data[0]
            self.logger.info('========== End get role entity ==========')
            return context

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start update role entity ==========')
        role_id = kwargs['role_id']

        name = request.POST.get('name', '')
        description = request.POST.get('description', '')

        params = {
            'name': name,
            'description': description,
            'is_page_level': True
        }

        url = api_settings.ROLE_DETAIL_PATH.format(role_id=role_id)
        is_success, status_code, status_message, data = RestFulClient.put(self.request, url, self._get_headers(),
                                                                          logger, params)
        if is_success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Updated role entity successfully'
            )
            self.logger.info('========== End update role entity ==========')
            return redirect('authentications:role_list')

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers
