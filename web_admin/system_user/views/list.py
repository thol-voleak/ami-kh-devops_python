from web_admin import api_settings
from web_admin import setup_logger, RestFulClient
from authentications.utils import get_auth_header
from authentications.apps import InvalidAccessToken

from django.shortcuts import render
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class ListView(TemplateView):
    template_name = "system_user/list.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = {
            'data': [],
            'created_msg': self.request.session.pop('system_user_create_msg', None),
            'del_msg': self.request.session.pop('system_user_delete_msg', None),
            'pw_msg': self.request.session.pop('system_user_change_password_msg', None)
        }
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        self.logger.info("========== Start searching system user ==========")
        username = request.POST.get('username')
        email = request.POST.get('email')
        params = {}
        if username:
            params['username'] = username
        if email:
            params['email'] = email

        status_code, status_message, data = self.search_system_user(username, email, None)

        if (status_code == "access_token_expire") or \
                (status_code == 'access_token_not_found') or \
                (status_code == 'invalid_access_token'):
            logger.info("{} for {} username".format(status_message, self.request.user))
            raise InvalidAccessToken(status_message)

        context['data'] = data
        context['username'] = username
        context['email'] = email
        self.logger.info("========== Finish searching system user ==========")
        return render(request, self.template_name, context)

    def search_system_user(self, username, email, user_id):
        params = {}

        if username is not '' and username is not None:
            params['username'] = username
        if email is not '' and email is not None:
            params['email'] = email
        if user_id is not '' and user_id is not None:
            params['user_id'] = user_id

        is_success, status_code, status_message, data = RestFulClient.post(self.request,
                                                                           api_settings.SEARCH_SYSTEM_USER,
                                                                           self._get_headers(), logger, params)

        return status_code, status_message, data

    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers
