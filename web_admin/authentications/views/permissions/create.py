from authentications.utils import get_auth_header
from web_admin import api_settings
from web_admin import setup_logger, RestFulClient

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from authentications.apps import InvalidAccessToken

import logging

logger = logging.getLogger(__name__)


class PermissionCreate(TemplateView):
    template_name = "permissions/create.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(PermissionCreate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PermissionCreate, self).get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start creating permission ==========')

        name = request.POST.get('name', '')
        description = request.POST.get('description', '')

        params = {
            'name': name,
            'description': description,
            'is_page_level': True
        }

        is_success, status_code, status_message, data = RestFulClient.post(self.request,
                                                                           api_settings.CREATE_PERMISSION_PATH,
                                                                           self._get_headers(), logger, params)
        if is_success:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Added data successfully'
            )
            self.logger.info('========== End creating permission ==========')
            return redirect('authentications:permissions_list')
        elif (status_code == "access_token_expire") or (status_code == 'access_token_not_found') or (
                        status_code == 'invalid_access_token'):
            logger.info("{} for {} username".format(status_message, self.request.user))
            raise InvalidAccessToken(status_message)
        else:
            return render(request, self.template_name)

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers
