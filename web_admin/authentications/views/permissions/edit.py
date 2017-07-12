from authentications.utils import get_auth_header
from web_admin import api_settings
from web_admin import setup_logger, RestFulClient
from authentications.apps import InvalidAccessToken

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class PermissionEditView(TemplateView):
    template_name = "permissions/edit.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(PermissionEditView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start get permission entity ==========')
        context = super(PermissionEditView, self).get_context_data(**kwargs)
        permission_id = context['permission_id']
        params = {
            'id': int(permission_id)
        }
        self.logger.info("Searching permission with [{}] id".format(permission_id))
        is_success, status_code, status_message, data = RestFulClient.post(request=self.request,
                                                                           url=api_settings.PERMISSION_LIST.format(permission_id=permission_id),
                                                                           headers=self._get_headers(),
                                                                           logger=logger, params=params)
        if is_success:
            context['permission'] = data[0]
            self.logger.info('========== End get permission entity ==========')
        else:
            if (status_code == "access_token_expire") or (status_code == 'access_token_not_found') or (
                        status_code == 'invalid_access_token'):
                logger.info("{} for {} username".format(status_message, self.request.user))
                raise InvalidAccessToken(status_message)
        return context

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start update permission entity ==========')
        permission_id = kwargs['permission_id']

        name = request.POST.get('name', '')
        description = request.POST.get('description', '')

        params = {
            'name': name,
            'description': description,
            'is_page_level': True
        }

        url = api_settings.PERMISSION_DETAIL_PATH.format(permission_id=permission_id)
        is_success, status_code, status_message, data = RestFulClient.put(self.request, url, self._get_headers(),
                                                                          logger, params)
        if is_success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Updated data successfully'
            )
            self.logger.info('========== End update permission entity ==========')
            return redirect('authentications:permissions_list')

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers
